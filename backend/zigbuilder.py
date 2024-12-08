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

    with open(os.path.join(metadata_directory, 'METADATA')) as f:
        metadata_lines = f.readlines()

    name = read_value('Name', metadata_lines)
    version = read_value('Version', metadata_lines)

    with tempfile.TemporaryDirectory() as temp_dir:
        wheel = os.path.join(wheel_directory, res)
        with ZipFile(wheel, 'r') as zf:
            print(zf.namelist())
            zf.extractall(temp_dir)
        
        os.remove(wheel)

        hashes = []       
        with tempfile.TemporaryDirectory() as zig_build_dir:
            for file in os.listdir(os.path.join(temp_dir, 'zig')):
                subprocess.call([
                    sys.executable, 
                    '-m', 
                    'ziglang', 
                    'build-lib', 
                    os.path.join(temp_dir, 'zig', file) 
                    ,'-dynamic'
                ], cwd=zig_build_dir)
            shutil.rmtree(os.path.join(temp_dir, 'zig'))

            for x in os.listdir(zig_build_dir):
                src = os.path.join(zig_build_dir, x)
                tgt = os.path.join(temp_dir, name, x)
                shutil.move(src, tgt)
                hashes.append(f'{os.path.join(name, x)},sha256={sha256_file_b64_nopad(tgt)},{os.path.getsize(tgt)}{os.linesep}')

        with open(os.path.join(temp_dir, f'{name}-{version}.dist-info', 'RECORD'), 'a') as f:
            f.writelines(hashes)

        shutil.make_archive(wheel, 'zip', temp_dir)
        shutil.move(f'{wheel}.zip', wheel)
        print(os.listdir(wheel_directory))

    return res


build_sdist = pb.build_sdist
get_requires_for_build_sdist = pb.get_requires_for_build_sdist
get_requires_for_build_wheel = pb.get_requires_for_build_wheel
prepare_metadata_for_build_wheel = pb.prepare_metadata_for_build_wheel
