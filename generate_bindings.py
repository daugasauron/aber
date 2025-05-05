import os
import tree_sitter_zig as tszig
from typing import Tuple
from tree_sitter import Language, Parser

ZIG_LANG = Language(tszig.language())
parser = Parser(ZIG_LANG)

class Argument:
    name: str
    typ: type

    def __init__(self, name: str, typ: type):
        self.name = name
        self.typ = typ

    def __repr__(self):
        return f'{self.name}: {str(self.typ.__name__)}'

class Function:
    name: str
    typ: type
    args: Tuple[Argument]

    def __init__(self, name: str, typ: type, args: Tuple[Argument]):
        self.name = name
        self.typ = typ
        self.args = args

    def __repr__(self):
        return f'def {self.name}({", ".join([x.__repr__() for x in self.args])}) -> {self.typ.__name__}:'

def read_value(node, byte_lines):
    start_row, start_col = node.start_point.row, node.start_point.column
    end_row, end_col = node.end_point.row, node.end_point.column
    
    if start_row == end_row:
        return byte_lines[start_row][start_col:end_col].decode('utf-8')
    
    lines = [byte_lines[start_row][start_col:]]

    for row in range(start_row + 1, end_row):
        lines.append(byte_lines[row])

    lines.append(byte_lines[end_row][:end_col])

    return b'\n'.join(lines).decode('utf-8')

def map_types(type_str):
    if type_str == 'i32':
        return int
    elif type_str == '[*:0]const u8':
        return str
    else:
        raise ArgumentError(f'Unknown type: {type_str}')
    

def parse_return_type(nodes, byte_lines):
    if 'builtin_type' in nodes:
        type_str = read_value(nodes['builtin_type'], byte_lines)
    elif 'pointer_type' in nodes:
        type_str =  read_value(nodes['pointer_type'], byte_lines)
    return map_types(type_str)

def parse_argument(node, byte_lines):
    name, type_str = read_value(node, byte_lines).split(': ')
    return Argument(name, map_types(type_str))

def parse_function(node, byte_lines):
    nodes = {x.type: x for x in node.children}
    
    name = read_value(nodes['identifier'], byte_lines)
    return_type = parse_return_type(nodes, byte_lines)
    arguments = [
        parse_argument(x, byte_lines) 
        for x in nodes['parameters'].children 
        if x.type == 'parameter'
    ]

    return Function(name, return_type, arguments)

    
def generate_from_file(file_name: str) -> None:
    with open(os.path.join('zig', file_name), 'rb') as f:
        file_bytes = f.read()
        tree = parser.parse(file_bytes)

        byte_lines = file_bytes.splitlines()

        function_nodes = [
            x for x in tree.root_node.children 
            if x.type == 'function_declaration'
        ]

        parsed_functions = [
            parse_function(x, byte_lines)
            for x in function_nodes
            if 'export' in [r.type for r in x.children]
        ]

        if not len(parsed_functions):
            return

        lib_name = file_name.replace('.zig', '')


        with open(os.path.join('aber', file.replace('.zig', '.py')), 'w') as out_f:
            out_f.write('# Generated from generate_bindings.py' + os.linesep)
            out_f.write('from aber.ziglib import ZigLib, zig_function' + os.linesep)
            out_f.write(os.linesep)
            out_f.write(f"lib = ZigLib('{lib_name}')" + os.linesep)

            for parsed_function in parsed_functions:
                out_f.write(os.linesep)
                out_f.write('@zig_function(lib)' + os.linesep)
                out_f.write(parsed_function.__repr__() + os.linesep)
                out_f.write('    pass' + os.linesep)

            out_f.write(os.linesep)


for file in os.listdir('zig'):
    if file.endswith('.zig') and file != 'build.zig':
        generate_from_file(file)
