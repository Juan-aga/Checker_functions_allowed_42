import sys
try:
    import clang.cindex
except:
    sys.exit("Clang library not installed.\nTry \"pip3 install libclang\"")

import os
import re
import get_library_definitions as gld

definitions = {}
calls = {}
extensions = [".c", ".h"]
exclude_path = [".git"]
only_definitions = ["MLX42", "minilibx"]
project = set()
allows = []



class checked_functions:
    def __init__(self):
        self.functions = {"declarations": {}, "calls": {}, "allows": [], "undefined":{}}
    def add(self, key, name, file, line):
        if not key in self.functions:
            print(f'Not key {key} in functions.')
            return
        if name in self.functions[key]:
            self.functions[key][name]['file'].append(file)
            self.functions[key][name]['line'].append(line)
        else:
            self.functions[key][name] = {'file':[file], 'line':[line]}
    def print(self, key):
        print(f'{key} functions:')
        for name, info in self.functions[key].items():
            print(f'\t{name}')
            file = info['file']
            line = info['line']
            for i in range(len(file)):
                print(f'\t\tFile: {file[i]}\t\tLine: {line[i]}')


checked = checked_functions()

class get_allowed:
    def __init__(self):
        self.allowed_functions = {
                "libft": ["malloc", "free", "write", "del", "f"],
                "get_next_line": ["read", "malloc", "free"],
                "libftprintf": ["va_start", "va_arg", "va_copy", "va_end"],
                "minitalk": ["write", "signal", "sigemptyset", "sigaddset", "sigaction", "kill", "getpid", "malloc", "free", "pause", "sleep", "usleep", "exit"],
                "pipex": ["open", "close", "read", "write", "malloc", "free", "perror", "strerror", "access", "dup", "dup2", "execve", "exit", "fork", "pipe", "unlink", "wait", "waitpid"],
                "push_swap": ["read", "write", "malloc", "free", "exit"],
                "so_long": ["open", "close", "read", "write", "malloc", "free", "perror", "strerror", "exit"],
                "fdf": ["open", "close", "read", "write", "malloc", "free", "perror", "strerror", "exit"],
                "fractol": ["open", "close", "read", "write", "malloc", "free", "perror", "strerror", "exit"],
                "philo": ["memset", "printf", "malloc", "free", "write", "usleep", "gettimeofday", "pthread_create", "pthread_detach", "pthread_join", "pthread_mutex_init", "pthread_mutex_destroy", "pthread_mutex_lock", "pthread_mutex_unlock"],
                "philo_bonus": ["memset", "printf", "malloc", "free", "write", "fork", "kill", "exit", "pthread_create", "pthread_detach", "pthread_join", "usleep", "gettimeofday", "waitpid", "sem_open", "sem_close", "sem_post", "sem_wait", "sem_unlink"],
                "minishell": ["readline", "rl_clear_history", "rl_on_new_line", "rl_replace_line", "rl_redisplay", "add_history", "printf", "malloc", "free", "write", "access", "open", "read", "close", "fork", "wait", "waitpid", "wait3", "wait4", "signal", "sigaction", "sigemptyset", "sigaddset", "kill", "exit", "getcwd", "chdir", "stat", "lstat", "fstat", "unlink", "execve", "dup", "dup2", "pipe", "opendir", "readdir", "closedir", "strerror", "perror", "isatty", "ttyname", "ttyslot", "ioctl", "getenv", "tcsetattr", "tcgetattr", "tgetent", "tgetflag", "tgetnum", "tgetstr", "tgoto", "tputs"],
                "cub3D": ["open", "close", "read", "write", "printf", "malloc", "free", "perror", "strerror", "exit"],
                "miniRT": ["open", "close", "read", "write", "printf", "malloc", "free", "perror", "strerror",     "exit"]
        }
        
    def functions(self, project):
        if project in self.allowed_functions:
            return self.allowed_functions[project]
        else:
            return []

def ft_get_functions(file_name):
    index = clang.cindex.Index.create()
    code = index.parse(file_name)
    name_split = file_name.split(os.path.sep)
    for node in code.cursor.walk_preorder():
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            if node.location.file and str(node.location.file) == file_name:
                checked.add("declarations", node.spelling, file_name, node.location.line)
        elif node.kind == clang.cindex.CursorKind.CALL_EXPR:
            if not any(only in only_definitions for only in name_split):
                checked.add("calls", node.spelling, file_name, node.location.line)

def functions(path):
    for files in ft_list_files(path):
        ft_get_functions(files)
    allowed = get_allowed()
    for project_name in project:
        checked.functions['allows'].extend(allowed.functions(project_name))
        if project_name in ["fractol", "sol_long", "fdf", "cub3D", "miniRT"]:
            checked.functions['allows'].extend(gld.get_library_definitions("math.h"))

def ft_list_files(path):
    try:
        directory = os.listdir(path)
    except:
        print(f'No valid path: {path}')
        exit(1)
    for file_name in directory:
        if file_name in exclude_path:
            continue
        file_path = os.path.join(path, file_name)
        path_split = file_path.split(os.path.sep)
        if os.path.isdir(file_path) and not file_name in exclude_path:
            for new_files in ft_list_files(file_path):
                yield new_files
        elif os.path.isfile(file_path):
            if os.path.splitext(file_path)[1] in extensions:
               yield file_path
            elif file_name == "Makefile" and not any(exclude in only_definitions for exclude in path_split):
                print("Makefile in: ", file_path)
                ft_get_project(file_path)
    if "get_next_line.h" in directory:
        project.add("get_next_line")

def ft_get_project(make):
    try:
        with open(make, 'r') as f:
            makefile = f.read()
    except:
        print(f'Failed to open {path}')
        exit(1)
    name = 'NAME'
    pattern = r'^\s*{}(?:\s*)[:]?=(?:\s*)(.*)$'.format(name)
    find = re.search(pattern, makefile, re.MULTILINE)
    global project
    if find:
        project.add(os.path.splitext(find.group(1))[0])
    else:
        print(f'{variable_name} not find in {make}')
    if any(check in ["server", "client"] for check in project):
        project.add("minitalk")
        project -= {"server", "client"}

def ft_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument(
            "-p",
            "--path",
            help="PATH to check",
            default = os.getcwd()
            )
    return parse.parse_args()

if __name__ == "__main__":
    import argparse
    args = ft_parser()
    functions(args.path)
    c = [call for call in calls if call not in definitions]
    print("Undefined:")
    for call in c:
        if call and call not in allows:
            print(f'Functions: {call}, File: {calls[call]["file"]}, Line: {calls[call]["line"]}')
#    print("Used:")
#    for call in calls:
#        print(f'Functions: {call}, File: {calls[call]["file"]}, Line: {calls[call]["line"]}')
    print(f'Project: {project}')
    checked.print("declarations")
    checked.print('calls')
    print(f'Allows: {checked.functions["allows"]}')

