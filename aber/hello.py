import os
from aber.ziglib import ZigLib, zig_function

hello_lib = ZigLib('hello')

@zig_function(hello_lib)
def zig_add(a: int, b: int) -> int:
    pass


@zig_function(hello_lib)
def zig_hello(a: str) -> str:
    pass
   

if __name__ == '__main__':
    print(f'zig_add(1, 2): {zig_add(1, 2)}')
    print(f'zig_hello("yeah"): {zig_hello("yeah")}')

