# Generated from generate_bindings.py
from aber.ziglib import ZigLib, zig_function

lib = ZigLib('hello')

@zig_function(lib)
def zig_add(a: int, b: int) -> int:
    pass

@zig_function(lib)
def zig_mult(a: int, b: int) -> int:
    pass

@zig_function(lib)
def zig_hello(str: str) -> str:
    pass

