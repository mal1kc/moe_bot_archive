from types import ModuleType
import win32api
import win32process
import importlib


"""
base_module: have 2 dynamicly created variable
module 1: imports base_module
module 2: imports base_module
"""
module1_name = "reimport_test_module1"
module2_name = "reimport_test_module2"


def get_ram_usage():
    handle = win32api.GetCurrentProcess()
    return win32process.GetProcessMemoryInfo(handle)["WorkingSetSize"] / 1024 / 1024


def test1():
    """
    we can see python's garbage collector is not deleting the module
    if we want to reimport the module we have to importlib.reload it
    """
    print("ram usage in start: {:.6f} MB".format(get_ram_usage()))

    s1 = load_module(module1_name)
    s1.do_stuff = lambda: print("new stuff")
    s1 = None

    print("ram usage after first None ref: {:.6f} MB".format(get_ram_usage()))

    s1 = load_module(module1_name)
    s1.do_stuff()
    print("ram usage after first reimport call: {:.6f} MB".format(get_ram_usage()))

    s1 = None
    print("ram usage after first reimport None ref: {:.6f} MB".format(get_ram_usage()))

    s1 = load_module(module1_name)
    s1 = importlib.reload(s1)
    s1.do_stuff()

    print("ram usage after first reimport reload call: {:.6f} MB".format(get_ram_usage()))


def test2():
    """ """
    s1 = load_module(module1_name)
    s1.do_stuff()
    s1.change_var()

    print("ram usage after first reimport reload call: {:.6f} MB".format(get_ram_usage()))

    s2 = load_module(module2_name)
    s2.do_stuff()


def test3():
    s1 = load_module(module1_name)
    s1 = importlib.reload(s1)
    stuff1_1, stuff1_2 = s1.get_stuff()
    s1.change_var()
    new_stuff1_1, new_stuff1_2 = s1.get_stuff()

    s2 = load_module(module2_name)
    s2 = importlib.reload(s2)
    stuff2_1, stuff2_1 = s2.get_stuff()
    s1.change_var()
    new_stuff2_1, new_stuff2_2 = s2.get_stuff()

    # print table of vars
    print("module name | var name | old value | new value")
    print("module1 | dynamicly_created_variable | {} | {}".format(stuff1_1, new_stuff1_1))
    print("module1 | dynamicly_created_variable_list | {} | {}".format(stuff1_2, new_stuff1_2))
    print("module2 | dynamicly_created_variable | {} | {}".format(stuff2_1, new_stuff2_1))

    # ----------------

    s1 = load_module(module1_name)
    s1 = importlib.reload(s1)
    stuff1_1, stuff1_2 = s1.get_stuff()
    s1.delete_var()
    new_stuff1_1, new_stuff1_2 = s1.get_stuff()

    s2 = load_module(module2_name)
    s2 = importlib.reload(s2)
    stuff2_1, stuff2_1 = s2.get_stuff()
    s1.delete_var()
    new_stuff2_1, new_stuff2_2 = s2.get_stuff()

    # print table of vars
    print("module name | var name | old value | new value")
    print("module1 | dynamicly_created_variable | {} | {}".format(stuff1_1, new_stuff1_1))
    print("module1 | dynamicly_created_variable_list | {} | {}".format(stuff1_2, new_stuff1_2))
    print("module2 | dynamicly_created_variable | {} | {}".format(stuff2_1, new_stuff2_1))


def load_module(module_name) -> ModuleType:
    return importlib.import_module(module_name)


if __name__ == "__main__":
    test3()
