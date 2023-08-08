# --- queue.Queue() ile ---
# import random
# import queue
# import threading
# import time

# def number_generator(out_queue:queue.Queue, command_queue:queue.Queue):
#     def generate_number():
#         return random.randint(1, 100)

#     while True:
#         try:
#             command = command_queue.get(timeout=1)
#             print(f"number_generator -> Command: {command}")
#             if command == "close":
#                 print("number_generator -> Terminating...")
#                 break
#         except queue.Empty:
#             print("number_generator -> command_queue Timeout.")
#             pass
#         number = generate_number()
#         out_queue.put(number)


# def number_checker(in_queue:queue.Queue, out_queue:queue.Queue, command_queue:queue.Queue):
#     counter = 0
#     while True:
#         try:
#             number = in_queue.get(timeout=1)
#             print(f"number_checker -> Received: {number}")
#         except queue.Empty:
#             print("number_checker -> Timeout. Retrying...")
#             continue

#         if counter == 10:
#             print("number_checker -> 10 numbers printed. Terminating...")
#             command_queue.put("close")
#             command_queue.put("close")
#             break
#         if 3 <= number <= 30:
#             out_queue.put(number)
#             print(f"number_checker -> Sent: {number}")
#             counter += 1

# def number_printer(number_queue: queue.Queue):
#     received_numbers = set()
#     timeout_counter = 0
#     while len(received_numbers) < 10:
#         try:
#             number = number_queue.get(timeout=1)
#             print(f"number_printer -> Received: {number}")
#         except queue.Empty:
#             timeout_counter += 1
#             if timeout_counter == 30:
#                 print("number_printer -> Timeout counter reached. Terminating...")
#                 break
#             print("number_printer -> Timeout. Retrying...")
#             continue

#         received_numbers.add(number)
#         print(f"number_printer -> One of the best numbers: {number}")
#     print("number_printer -> All processes terminated.")

# def main():
#     number_queue = queue.Queue()
#     command_queue = queue.Queue()

#     generator_thread = threading.Thread(target=number_generator, args=(number_queue, command_queue))
#     checker_thread = threading.Thread(target=number_checker, args=(number_queue, number_queue, command_queue))
#     printer_thread = threading.Thread(target=number_printer, args=(number_queue,))

#     generator_thread.start()
#     checker_thread.start()
#     printer_thread.start()

#     time.sleep(5)  # Allow some time for execution

#     command_queue.put("close")

#     generator_thread.join()
#     checker_thread.join()
#     printer_thread.join()

# if __name__ == "__main__":
#     main()

# --- multiprocessing.Value() ile ---

import multiprocessing
import random
import time


def str_command(command):
    _str = ""
    for i in range(len(command)):
        _str += command[i]
    return _str


def number_generator(number, command):
    def generate_number():
        return random.randint(1, 100)

    while True:
        if str_command(command) == "close":
            print("number_generator -> Terminating...")
            break
        number.value = generate_number()
        sleep_time = random.randint(1, 5)
        time.sleep(sleep_time / 5)


def number_checker(number_in, number_out, command):
    while True:
        print(f"number_checker -> Received: {number_in.value}")
        if str_command(command) == "close":
            print("number_checker -> 10 numbers printed. Terminating...")
            break
        if 3 <= number_in.value <= 30:
            print(f"number_checker -> Sent: {number_in.value}")
            number_out.value = number_in.value
        time.sleep(0.1)


def number_printer(best_number, command):
    received_numbers = set()
    while len(received_numbers) < 10:
        print(f"number_printer -> Received: {best_number.value}")
        received_numbers.add(best_number.value)
        print(f"number_printer -> One of the best numbers: {best_number.value}")
        time.sleep(0.1)
    for i in range(len("close")):
        command[i] = "close"[i]

    print("number_printer -> All processes terminated.")


def main():
    number = multiprocessing.Value("i", 0)
    best_number = multiprocessing.Value("i", 0)

    command = multiprocessing.Array("u", "".join([" " * len("close")]))  # 'u' -> unicode character

    print("main -> Processes started.")
    print(f"main -> {number.value=} ")  # type: ignore
    print(f"main -> {command[:]=} ")  # type: ignore
    print(f"main -> {best_number.value=} ")  # type: ignore
    time.sleep(5)
    generator_process = multiprocessing.Process(target=number_generator, args=(number, command))
    checker_process = multiprocessing.Process(target=number_checker, args=(number, best_number, command))
    printer_process = multiprocessing.Process(target=number_printer, args=(best_number, command))

    generator_process.start()
    checker_process.start()
    printer_process.start()
    time.sleep(0.1)  # Allow some time for execution

    generator_process.join()
    checker_process.join()
    printer_process.join()


if __name__ == "__main__":
    main()
