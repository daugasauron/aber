const std = @import("std");

export fn zig_add(a: i32, b: i32) i32 {
    return a + b;
}

export fn zig_hello(str: [*:0]const u8) [*:0]const u8 {
    const hello: []const u8 = "Hello ";
    const slice: []const u8 = str[0..std.mem.len(str)];

    const allocator = std.heap.page_allocator;
    const result_len = hello.len + slice.len;
    const result = allocator.alloc(u8, result_len + 1) catch {
        return "error";
    };

    std.mem.copyForwards(u8, result, hello);
    std.mem.copyForwards(u8, result[hello.len..], slice);
    result[result_len] = 0;

    return @ptrCast(result);
}
