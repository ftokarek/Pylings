"""
Threading Exercise 3 (threading3.py)
This exercise introduces `threading.Semaphore` for resource management.
Limit concurrent access to a resource using a semaphore.
Follow the TODO instructions and complete each section.
"""

import threading
import time

semaphore = threading.Semaphore(3)  # Limit concurrent access to 3 threads
active_threads = 0  # Track active threads
active_threads_lock = threading.Lock()  # Lock to modify active_threads safely
max_threads_reached = 0  # Track the highest number of concurrent threads


# TODO: Implement `access_resource` to enforce semaphore limits.
def access_resource(thread_id):
    """
    This function should:
    - Acquire the semaphore before proceeding.
    - Safely increment `active_threads` inside `active_threads_lock`.
    - Ensure no more than 3 threads are active at a time.
    - Print `"Thread {thread_id} accessing resource"`.
    - Sleep for 0.1 seconds to simulate work.
    - Print `"Thread {thread_id} done"`.
    - Safely decrement `active_threads` and release the semaphore.
    """
    global active_threads, max_threads_reached

    # acquire semaphore slot
    semaphore.acquire()
    try:
        with active_threads_lock:
            active_threads += 1
            if active_threads > max_threads_reached:
                max_threads_reached = active_threads

            # check concurrency condition
            assert active_threads <= 3, f"Too many threads active! ({active_threads})"

        print(f"Thread {thread_id} accessing resource")
        time.sleep(0.1)
        print(f"Thread {thread_id} done")

        with active_threads_lock:
            active_threads -= 1
    finally:
        # release semaphore slot
        semaphore.release()


def main():
    """
    The main function should:
    - Create 6 threads that run `access_resource`
    - Ensure all threads finish execution using `.join()`
    - Verify that no more than 3 threads access the resource at the same time
    """

    global active_threads, max_threads_reached
    active_threads = 0  # Reset counter before running
    max_threads_reached = 0  # Reset max tracking

    threads = []

    for i in range(6):
        thread = threading.Thread(target=access_resource, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Ensure active_threads is back to zero
    assert active_threads == 0, f"Error: active_threads should be 0 after execution, but got {active_threads}"

    # Ensure max concurrent threads never exceeded 3
    assert 0 < max_threads_reached <= 3, (
        f"Error: More than 3 threads ran concurrently! Max observed: {max_threads_reached}"
    )

    print(f"Max concurrent threads observed: {max_threads_reached}")


if __name__ == "__main__":
    main()
