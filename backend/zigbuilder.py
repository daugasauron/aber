import os
import sys
import shutil
import base64
import hashlib
import tempfile
import subprocess
import poetry.core.masonry.api as pb
from zipfile import ZipFile
from typing import Any

def read_value(key, lines):
    for line in lines:
        if line.startswith(key):
            return line.split(':')[1].strip()

def sha256_file_b64_nopad(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256_hash.update(chunk)
    
    hash_bytes = sha256_hash.digest()
    return base64.urlsafe_b64encode(hash_bytes).rstrip(b'=').decode('utf-8')

def build_wheel(
        wheel_directory: str, 
        config_settings: dict[str, Any] | None = None, 
        metadata_directory: str | None = None
) -> str:

    res = pb.build_wheel(wheel_directory, config_settings, metadata_directory)
    name, version, *_ = res.split('-')

    with tempfile.TemporaryDirectory() as temp_dir:
        wheel = os.path.join(wheel_directory, res)
        with ZipFile(wheel, 'r') as zf:
            zf.extractall(temp_dir)
        
        os.remove(wheel)

        subprocess.call([
            sys.executable,
            '-m',
            'ziglang',
            'build',
        ], cwd=os.path.join(temp_dir, 'zig'))

        shutil.rmtree(os.path.join(temp_dir, 'zig', '.zig-cache'))

        print(os.listdir(os.path.join(temp_dir, 'zig', 'zig-out')))

        lib_dir = os.path.join(temp_dir, 'zig', 'zig-out', 'lib')
        hashes = []
        for x in os.listdir(lib_dir):
            tgt = os.path.join(lib_dir, x)
            hashes.append(f'{os.path.join(name, x)},sha256={sha256_file_b64_nopad(tgt)},{os.path.getsize(tgt)}{os.linesep}')

        with open(os.path.join(temp_dir, f'{name}-{version}.dist-info', 'RECORD'), 'a') as f:
            f.writelines(hashes)

        shutil.make_archive(wheel, 'zip', temp_dir)
        shutil.move(f'{wheel}.zip', wheel)

    return res


build_sdist = pb.build_sdist
get_requires_for_build_sdist = pb.get_requires_for_build_sdist
get_requires_for_build_wheel = pb.get_requires_for_build_wheel
prepare_metadata_for_build_wheel = pb.prepare_metadata_for_build_wheel
