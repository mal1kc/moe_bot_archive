from pprint import pprint
from reimport_test_base_module import dynamicly_created_variable, dynamicly_created_variable_list


def do_stuff():
    print("doing stuff")
    print(dynamicly_created_variable)
    pprint(dynamicly_created_variable_list)
    print("done doing stuff")


def get_stuff():
    return dynamicly_created_variable, dynamicly_created_variable_list
