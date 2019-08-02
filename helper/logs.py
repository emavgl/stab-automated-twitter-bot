import os


def read_file(file_path: str):
    if not os.path.exists(file_path):
        return []
    with open(file_path) as file:
        return set(file.read().split('\n'))

def write_line_on_file(file_path: str, line: str):
    with open(file_path, 'a') as file:
        file.write(line + '\n')