"""
Threading Exercise 1 (threading1.py)
This program spawns multiple threads that each run for at least 1 second.
Each thread returns how much time it took to complete.
The program should wait until all the spawned threads have finished
and should collect their return values into a list.

Follow the TODO instructions and complete each section.
"""

import threading
import time


def worker(thread_id, results, lock):
    """
    This function represents the work done by each thread.
    It should:
    - Record the start time
    - Sleep for 1 second
    - Print "Thread {thread_id} done"
    - Return the elapsed time (store it in results)
    """
    start_time = time.time()
    time.sleep(1)
    elapsed = time.time() - start_time
    print(f"Thread {thread_id} done")
    # zapisz wynik bezpiecznie do listy
    with lock:
        results[thread_id] = elapsed


def main():
    """
    The main function should:
    - Create and start 5 threads
    - Ensure all threads finish execution using `.join()`
    - Collect their return values in the `results` list
    """
    threads = []
    results = [None] * 5  # miejsce na wyniki
    lock = threading.Lock()

    for i in range(5):
        thread = threading.Thread(target=worker, args=(i, results, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    if len(results) != 5 or any(r is None for r in results):
        raise RuntimeError("Oh no! Some thread isn't done yet!")

    print()
    for i, result in enumerate(results):
        print(f"Thread {i} took {result:.2f} seconds")


if __name__ == "__main__":
    main()
