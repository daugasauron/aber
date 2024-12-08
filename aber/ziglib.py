import os
import builtins
import platform
from ctypes import CDLL, POINTER, c_char, c_char_p, c_int, create_string_buffer
from inspect import signature, Parameter
from typing import Set, Callable, Any

LIB_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'lib'))

def _annotation_to_c_type(type_annotation): 
    match type_annotation:
        case builtins.int:
            return c_int
        case builtins.str:
            return c_char_p
        case _:
            raise Exception(f'Type annotation {param.annotation} not supported')


class ZigLib:
    lib: CDLL

    def __init__(self, lib_name: str):

        match platform.system():
            case 'Darwin':
                name = f'lib{lib_name}.dylib'
            case 'Windows':
                name = f'{lib_name}.dll'
            case _:
                name = f'lib{lib_name}.so'

        self.lib = CDLL(os.path.join(LIB_DIR, name))
        self.initialized = set()

    def initialize(self, func: Callable) -> None:
        lib_fn = getattr(self.lib, func.__name__)
        sig = signature(func)
        
        lib_fn.restype = _annotation_to_c_type(sig.return_annotation)
        lib_fn.argtypes = [_annotation_to_c_type(x.annotation) for x in sig.parameters.values()]


def _map_arg(arg):
    match arg:
        case int():
            return arg
        case str():
            return create_string_buffer(arg.encode('utf-8'))
        case _:
            raise Exception(f'Runtime argument type {type(arg)} not supported')


def zig_function(zig_lib: ZigLib):
    def decorator(func):

        zig_lib.initialize(func)

        def wrapper(*args):
            args = [_map_arg(x) for x in args]
            fun = getattr(zig_lib.lib, func.__name__)
            res = fun(*args)
            
            match res:
                case bytes():
                    return res.decode('utf-8')
                case int():
                    return res
                case _:
                    raise Exception(f'Return type {type(res)} not supported')

        return wrapper

    return decorator
