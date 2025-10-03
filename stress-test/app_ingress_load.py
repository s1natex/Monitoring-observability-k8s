#!/usr/bin/env python3
import argparse, random, time, threading, queue, sys
from collections import Counter, defaultdict
import requests

def pct(n, d): return (100.0 * n / d) if d else 0.0

def weighted_choice(weights, labels):
    # weights normalized internally
    s = sum(weights)
    r = random.random() * s
    upto = 0.0
    for w, lbl in zip(weights, labels):
        upto += w
        if upto >= r:
            return lbl
    return labels[-1]

def p95(values):
    if not values: return 0.0
    values = sorted(values)
    k = int(round(0.95 * (len(values)-1)))
    return values[k]

class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.started = 0
        self.done = 0
        self.errors = 0
        self.latencies = []
        self.by_code = Counter()
        self.by_service = Counter()
        self.exceptions = 0

    def add(self, service, code, latency_s):
        with self.lock:
            self.done += 1
            self.by_code[code] += 1
            self.by_service[service] += 1
            self.latencies.append(latency_s)

    def add_exc(self):
        with self.lock:
            self.exceptions += 1

def make_task(args):
    svc = weighted_choice(args.mix, ["frontend", "errors", "latency"])
    if svc == "frontend":
        url = args.frontend.rstrip("/") + "/"
    elif svc == "errors":
        want_5xx = random.random() < args.error_rate
        code = args.error_5xx_code if want_5xx else 200
        url = f"{args.errors.rstrip('/')}/?code={code}"
    else:  # latency
        ms = random.randint(args.latency_ms_min, args.latency_ms_max)
        url = f"{args.latency.rstrip('/')}/?ms={ms}&code={args.latency_code}"
    return svc, url

def worker(name, task_q: queue.Queue, stats: Stats, timeout):
    sess = requests.Session()
    while True:
        item = task_q.get()
        if item is None:
            task_q.task_done()
            return
        svc, url = item
        t0 = time.perf_counter()
        try:
            r = sess.get(url, timeout=timeout)
            latency = time.perf_counter() - t0
            stats.add(svc, r.status_code, latency)
        except Exception:
            stats.add_exc()
        finally:
            task_q.task_done()

def main():
    ap = argparse.ArgumentParser(description="Ingress load generator for frontend/api/latency services")
    ap.add_argument("--frontend", default="http://localhost", help="Frontend ingress base (default: http://localhost)")
    ap.add_argument("--errors",   default="http://localhost/api", help="Errors ingress base (default: http://localhost/api)")
    ap.add_argument("--latency",  default="http://localhost/latency", help="Latency ingress base (default: http://localhost/latency)")

    ap.add_argument("--duration", type=int, default=60, help="Test duration seconds (default: 60)")
    ap.add_argument("--rps", type=float, default=20.0, help="Target requests per second overall (default: 20)")
    ap.add_argument("--mix", nargs=3, type=float, metavar=("FRONTEND","ERRORS","LATENCY"),
                     default=[0.5, 0.25, 0.25], help="Traffic mix weights (default: 0.5 0.25 0.25)")

    ap.add_argument("--error-rate", type=float, default=0.10, help="Fraction of /api hits that are 5xx (default: 0.10)")
    ap.add_argument("--error-5xx-code", type=int, default=500, help="5xx code to use on /api (default: 500)")

    ap.add_argument("--latency-ms", nargs=2, type=int, metavar=("MIN","MAX"), default=[20, 500],
                    help="Latency range for /latency (ms) (default: 20 500)")
    ap.add_argument("--latency-code", type=int, default=200, help="Status code for /latency (default: 200)")

    ap.add_argument("--timeout", type=float, default=3.0, help="Per-request timeout seconds (default: 3.0)")
    ap.add_argument("--concurrency", type=int, default=0, help="Worker threads (default: auto = min(32, ceil(2*rps)))")
    args = ap.parse_args()

    args.latency_ms_min, args.latency_ms_max = args.latency_ms
    # normalize mix if needed
    sm = sum(args.mix)
    if sm <= 0:
        args.mix = [1.0, 0.0, 0.0]
    else:
        args.mix = [m/sm for m in args.mix]

    if args.concurrency <= 0:
        args.concurrency = max(1, min(32, int(args.rps*2 + 0.5)))

    stats = Stats()
    qtasks = queue.Queue(maxsize=int(max(10, args.rps * 2)))

    # workers
    threads = []
    for i in range(args.concurrency):
        t = threading.Thread(target=worker, args=(f"w{i}", qtasks, stats, args.timeout), daemon=True)
        t.start()
        threads.append(t)

    # feeder at target RPS
    interval = 1.0 / args.rps if args.rps > 0 else 0.0
    deadline = time.time() + args.duration
    next_t = time.time()

    try:
        while time.time() < deadline:
            svc, url = make_task(args)
            stats.started += 1
            try:
                qtasks.put((svc, url), timeout=1.0)
            except queue.Full:
                # backpressure: drop this tick
                pass
            if interval > 0:
                next_t += interval
                sleep_for = next_t - time.time()
                if sleep_for > 0:
                    time.sleep(sleep_for)
            else:
                time.sleep(0.001)
    except KeyboardInterrupt:
        pass

    # drain & stop
    qtasks.join()
    for _ in threads:
        qtasks.put(None)
    for t in threads:
        t.join(timeout=1.0)

    # summary
    with stats.lock:
        total = stats.done
        codes_sorted = sorted(stats.by_code.items())
        svc_sorted = sorted(stats.by_service.items())
        avg = (sum(stats.latencies)/len(stats.latencies)) if stats.latencies else 0.0
        p95v = p95(stats.latencies)

    print("\n=== Load Summary ===")
    print(f"Duration: {args.duration}s   Target RPS: {args.rps:.1f}   Concurrency: {args.concurrency}")
    print(f"Started: {stats.started}   Completed: {total}   Exceptions: {stats.exceptions}")
    print("By service:", ", ".join(f"{k}={v}" for k,v in svc_sorted) or "none")
    print("By status :", ", ".join(f"{k}={v}" for k,v in codes_sorted) or "none")
    print(f"Latency   : avg={avg*1000:.1f} ms   p95={p95v*1000:.1f} ms")
    print("====================\n")

if __name__ == "__main__":
    main()
