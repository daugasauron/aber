import os
import sys
import subprocess

def _library(file_name: str) -> str:
    lib_name = file_name[:-4] # drop .zig
    return f'''
    b.installArtifact(
        b.addSharedLibrary(.{{
            .name = "{lib_name}",
            .target = b.standardTargetOptions(.{{}}),
            .optimize = b.standardOptimizeOption(.{{}}),
            .root_source_file = b.path("zig/{file_name}"),
        }})
    );
    '''

zig_libs = os.linesep.join([
    _library(x) 
    for x in os.listdir('zig') 
    if x.endswith('.zig')
])

build = f'''
const std = @import("std");
pub fn build(b: *std.Build) void {{
{zig_libs}

}}'''

with open('build.zig', 'w') as f:
    f.write(build)
    
subprocess.call([sys.executable, "-m", "ziglang", "build", "--prefix", "."])
