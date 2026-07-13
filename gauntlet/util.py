from typing import TypeVar
import os

T = TypeVar("T")

def format_value(value) -> str:
    if value is None:
        return ""
    if type(value) is str:
        return f'"{value}"'
    elif type(value) is bool:
        return "OK" if value else "ERROR"
    elif isinstance(value, Exception):
        return f"Exception: {value}"
    return str(value)


def console_color(text: str, code: str) -> str:
    if code == 'w':
        return text

    return {
        "rb": "\033[41m",
        "gb": "\033[42m",
        "yb": "\033[43m",
        "r": "\033[31m",
        "g": "\033[32m",
        "y": "\033[33m",
        "b": "\033[34m",
        "m": "\033[35m",
        "c": "\033[36m",
    }[code] + text + "\033[0m"

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
        
