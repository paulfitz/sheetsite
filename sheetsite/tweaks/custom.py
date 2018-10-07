'''
Apply a custom tweak.  Expects my_script_name.py in same dir as .yml, with a the_method
method that will receive wb, params.

tweaks:
  custom:
    script: my_script_name
    method: the_method
    arg1: val1
    ...

'''

import importlib
import os
import sys

sys.path.append(os.getcwd())

def apply(wb, params):
    script = params['script']
    method = params['method']
    module = importlib.import_module(script)
    method_definition = getattr(module, method)
    return method_definition(wb, params)

