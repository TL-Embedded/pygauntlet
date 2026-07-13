from typing import TypeVar
import os

T = TypeVar("T")

def format_value(value) -> str:
    if type(value) is str:
        return f'"{value}"'
    elif type(value) is bool:
        return "OK" if value else "ERROR"
    return str(value)

def console_color(code: str) -> str:
    return {
        "r": "\033[31m",
        "g": "\033[32m",
        "y": "\033[33m",
        "b": "\033[34m",
        "m": "\033[35m",
        "c": "\033[36m",
        "w": "\033[0m",
    }[code]


def free_filename(path: str, default_extn: str = ".md"):

    head, tail = os.path.split(path)
    
    if head:
        os.makedirs(head, exist_ok=True)

    name, extn = os.path.splitext(tail)
    
    if extn == "":
        extn = default_extn

    fnames = os.listdir(head)

    for i in range(1000000):
        tail = f"{name}.{i}{extn}"
        if tail not in fnames:
            return os.path.join(head, tail)
        
