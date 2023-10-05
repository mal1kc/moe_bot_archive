import os
import time
import psutil

# test python object memory life
# create 1000000 object and delete them
# save memory usage
# assign half of them to None
# save memory usage
# del None objects
# save memory usage
# del all objects
# save memory usage
# print memory usage for each step
# the methods are should be inplace


def how_long_takes(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start} seconds")

    return wrapper


class TestClass(object):
    def __init__(self, name):
        self.name = name


def generate_count_str(count: int, base_str: str) -> str:
    return base_str + str(count)


def memory_usage_psutil():
    # return the memory usage in MB
    process = psutil.Process(os.getpid())
    return process.memory_info()[0] / float(2**20)


# methods with for loops


@how_long_takes
def main(max_count: int):
    obj_list = []
    times = []

    @how_long_takes
    def create_objects(count: int):
        for i in range(count):
            obj_list.append(TestClass(generate_count_str(i, "obj")))

    @how_long_takes
    def assign_half_to_none():
        for i in range(len(obj_list) // 2):
            obj_list[i] = None

    @how_long_takes
    def del_none_objects():
        """idk why but this method is so slower in bigger lists"""
        # 1000000 objects it will take 120 seconds
        for i in range(
            len(obj_list) - 1,
            -1,
            -1,
        ):
            cur_tm = time.time()
            if obj_list[i] is None:
                del obj_list[i]
            times.append(time.time() - cur_tm)

    @how_long_takes
    def del_all_objects():
        obj_list.clear()

    print(f"Memory usage before create_objects: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")
    create_objects(max_count)
    print(f"Memory usage after create_objects: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")
    assign_half_to_none()
    print(f"Memory usage after assign_half_to_none: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")
    del_none_objects()
    print(f"Memory usage after del_none_objects: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")
    del_all_objects()
    print(f"Memory usage after del_all_objects: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")
    print("Done")

    def check_timing_diffs():
        for i in range(len(times)):
            if times[i] > 0.001:
                print(f"index: {i}, time: {times[i]}")

    check_timing_diffs()


@how_long_takes
def main_with_list_compressions(max_count: int):
    obj_list = []
    # methods with list compressions
    # i can't created every method with list compressions

    @how_long_takes
    def create_objects_with_list_compressions(count: int) -> None:
        obj_list.extend([TestClass(generate_count_str(i, "obj")) for i in range(count)])

    @how_long_takes
    def assign_half_to_none() -> None:
        obj_list[: len(obj_list) // 2] = [None] * (len(obj_list) // 2)

    @how_long_takes
    def del_none_objects() -> None:
        filtered_list = list(filter(lambda x: x is not None, obj_list))
        obj_list.clear()
        obj_list.extend(filtered_list)

    @how_long_takes
    def del_all_objects_with_list_compressions() -> None:
        obj_list.clear()

    print(f"Memory usage before create_objects: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")

    create_objects_with_list_compressions(max_count)
    print(f"Memory usage after create_objects: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")

    assign_half_to_none()
    print(f"Memory usage after assign_half_to_none: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")

    del_none_objects()
    print(f"Memory usage after del_none_objects: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")

    del_all_objects_with_list_compressions()
    print(f"Memory usage after del_all_objects: {memory_usage_psutil()} MB, len(obj_list): {len(obj_list)}")

    print("Done")


if __name__ == "__main__":
    max_count = 1000000
    # print("Test with for loops")
    # main(max_count)
    # print("waiting 2 seconds ....")
    # time.sleep(2)
    print("Test with list compressions")
    main_with_list_compressions(max_count)
