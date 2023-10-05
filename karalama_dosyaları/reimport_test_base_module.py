import os

"""
this script is do import file
"""
dynamicly_created_variable = os.path.basename(__file__)
dynamicly_created_variable_list = [os.path.basename(__file__) for _ in range(2)]
