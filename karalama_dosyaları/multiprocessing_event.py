"""
trying to understand multiprocessing.Event
"""

import multiprocessing
import random
import time


def random_exiter(event):
    def generate_number():
        return random.randint(1, 100)

    while True:
        if event.is_set():
            print("random_exiter -> Terminating...")
            break
        print(f"random_exiter -> Generated: {generate_number()}")
        if generate_number() == 50:
            event.set()
        time.sleep(0.1)


def do_something(event):
    while True:
        print("do_something")
        time.sleep(10)
        if event.is_set():
            print("do_something -> Terminating...")
            break


if __name__ == "__main__":
    event = multiprocessing.Event()
    p1 = multiprocessing.Process(target=random_exiter, args=(event,))
    p2 = multiprocessing.Process(target=do_something, args=(event,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("All processes terminated.")
