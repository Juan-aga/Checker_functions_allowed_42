import subprocess
import os
import clang.cindex

declared = {}

def get_library_definitions(lib = None):
    if not lib:
        return None
    path = ft_get_library_path(lib)
    if not path:
        return None
    ft_get_declarations(path)
    return declared

def ft_get_library_path(lib):
    path = None
    result = subprocess.check_output(["gcc", "-E", "-Wp,-v", "-xc", "/dev/null"], stderr=subprocess.STDOUT, universal_newlines=True)
    for line in result.splitlines():
        new_path = os.path.join(line.strip(), lib)
        if os.path.exists(new_path):
            path = new_path
            break
    return path 

def ft_get_declarations(file_name):
    index = clang.cindex.Index.create()
    code = index.parse(file_name)
    for node in code.cursor.walk_preorder():
        declared[node.spelling] = {'file':node.location.file, 'line':node.location.line}

def ft_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "library",
            help = "Library to find declarations.",
            type = str,
            
            )
    return parser.parse_args()

if __name__ == "__main__":
    import argparse
    arg = ft_parser()
    get_library_definitions(arg.library)
    if declared:
        print(f'Find path to {arg.library}, Declarations:')
        for decl in declared:
            print(f'Funcion: {decl}, File: {declared[decl]["file"]}, line: {declared[decl]["line"]}')
    else:
        print(f'Not path found to {arg.library}')
