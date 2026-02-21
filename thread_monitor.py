import psutil
import time
import os
import sys


def get_total_active_threads():
    total_threads = 0
    # Iterate over all running processes
    for proc in psutil.process_iter(['num_threads']):
        try:
            # Extract thread count for this process
            threads = proc.info['num_threads']
            if threads:
                total_threads += threads
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Skip processes that died or are inaccessible during iteration
            continue
    return total_threads


def main():
    print(f"Monitoring system-wide active threads... (Press Ctrl+C to stop)")
    print(f"Platform: {os.name} ({sys.platform})")
    print("-" * 40)

    try:
        while True:
            count = get_total_active_threads()
            # Clear line and print new value (overwrite previous)
            sys.stdout.write(f"\rTotal Active Threads: {count:,}          ")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


if __name__ == "__main__":
    main()