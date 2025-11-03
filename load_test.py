import requests
import time
import threading
import argparse
from collections import deque
import datetime

start_time = time.time()
total_requests = 0
total_errors = 0
latencies = deque() 

lock = threading.Lock()

def make_request(url, stop_event):
    global total_requests, total_errors, latencies
    
    while not stop_event.is_set():
        request_start_time = time.time()
        try:
            response = requests.get(url, timeout=10)
            
            latency = (time.time() - request_start_time) * 1000
            
            with lock:
                total_requests += 1
                latencies.append(latency)
                if len(latencies) > 10000:
                    latencies.popleft()
                
                if response.status_code != 200:
                    total_errors += 1
                    
        except requests.exceptions.RequestException:
            with lock:
                total_requests += 1
                total_errors += 1
        
        time.sleep(0.01)

def print_stats(url, threads):

    print(f"Starting load test on {url} with {threads} threads...")
    print("Timestamp | Total Reqs | Errors | Avg Latency (ms) | Reqs/sec")
    print("-" * 70)
    
    last_check_time = time.time()
    last_check_requests = 0
    
    while True:
        time.sleep(10)
        
        current_time = time.time()
        duration_since_last = current_time - last_check_time
        
        with lock:
            current_total_requests = total_requests
            current_total_errors = total_errors
            current_latencies = list(latencies)
        
        if duration_since_last == 0:
            continue

        requests_since_last = current_total_requests - last_check_requests
        rps = requests_since_last / duration_since_last
        
        avg_latency = 0
        if current_latencies:
            avg_latency = sum(current_latencies) / len(current_latencies)
            
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        
        print(f"{timestamp} | {current_total_requests:<10} | {current_total_errors:<6} | {avg_latency:<16.2f} | {rps:<8.2f}")
        
        last_check_time = current_time
        last_check_requests = current_total_requests
        
        with lock:
            latencies.clear()

def main():
    parser = argparse.ArgumentParser(description="Simple Python Load Tester")
    parser.add_argument("--url", required=True, help="Target URL to test (e.g., http://localhost:5000/buses)")
    parser.add_argument("--threads", type=int, default=10, help="Number of concurrent threads (default: 10)")
    parser.add_argument("--duration", type=int, default=300, help="Duration of the test in seconds (default: 300)")
    args = parser.parse_args()

    stop_event = threading.Event()
    
    stats_thread = threading.Thread(target=print_stats, args=(args.url, args.threads), daemon=True)
    stats_thread.start()
    
    worker_threads = []
    for _ in range(args.threads):
        t = threading.Thread(target=make_request, args=(args.url, stop_event), daemon=True)
        t.start()
        worker_threads.append(t)
        
    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        print("Stopping worker threads...")
        stop_event.set()
        
        for t in worker_threads:
            t.join(timeout=1)
            
        print("\n--- FINAL RESULTS ---")
        total_time = time.time() - start_time
        final_rps = total_requests / total_time
        error_rate = 0
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            
        print(f"Total duration: {total_time:.2f} seconds")
        print(f"Total requests: {total_requests}")
        print(f"Total errors: {total_errors}")
        print(f"Error rate: {error_rate:.2f}%")
        print(f"Average RPS: {final_rps:.2f}")

if __name__ == "__main__":
    main()
