from typing import Callable, TypeVar
import re, time, datetime


T = TypeVar("T")
COLUMNS = [7, 32, 42, 30] # 120 chars wide once |'s are included.

class Gauntlet():
    
    def __init__(self, name: str = ""):
        self.name = name
        self.running = False

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()
    
    def start(self):
        self.running = True
        self.passed_tests = 0
        self.total_tests = 0
        self.start_time = time.time()
        ts = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
        self._log_header()
        self._log("Test start", ts)

    def stop(self):
        if self.running:
            self.running = False

            if self.passed_tests:
                self._log("Test passed", f"{self.passed_tests} / {self.total_tests} tests passed", 'g')
            else:
                self._log("Test failed", f"{self.passed_tests} / {self.total_tests} tests passed", 'r')

    def test(self, name: str, func: Callable[[],bool]) -> bool:
        predicate = lambda x: x
        return self._test_internal(name, func, predicate, "", None)

    def test_within(self, name: str, func: Callable[[], T], min: T = None, max: T = None, unit: str = None) -> bool:
        predicate = lambda x: (min == None or x >= min) and (max == None or x <= max)
        criteria = ("" if min == None else f"{self._format_value(min, unit)} < ") + "x" + ("" if max == None else f" > {self._format_value(max, unit)}")
        return self._test_internal(name, func, predicate, criteria, unit)

    def test_equal(self, name: str, func: Callable[[],T], expected: T, unit: str = None) -> bool:
        predicate = lambda x: x == expected
        criteria = f"x = {self._format_value(expected, unit)}"
        return self._test_internal(name, func, predicate, criteria, unit)

    def test_pattern(self, name: str, func: Callable[[], str], pattern: str) -> bool:
        predicate = lambda x: re.match(pattern, x) != None
        criteria = f"pattern matches \"{pattern}\""
        return self._test_internal(name, func, predicate, criteria, None)
    
    def test_log(self, name: str, func: Callable[[], T], unit: str = None) -> bool:
        predicate = lambda x: True
        return self._test_internal(name, func, predicate, unit)

    def _test_internal(self, name: str, value: Callable[[], T]|T, predicate: Callable[[T],bool], criteria: str, unit: str) -> bool:

        self.total_tests += 1
        if not self.running:
            return False
        
        if callable(value):
            self._log_row(["", name], temporary=True)
            try:
                value = value()
            except Exception as e:
                self._log_row([self._timestamp(), name, f"Exception occured, {e}", criteria])
                return False
        
        passed = predicate(value)
        if passed:
            self.passed_tests += 1
        self._log_row([self._timestamp(), name, self._format_value(value, unit), criteria], color=('w' if passed else 'r'))
        return passed

    def _format_value(self, value: T, unit: str) -> str:
        if type(value) is str:
            value = f'"{value}"'
        elif type(value) is bool:
            value = "OK" if value else "ERROR"
        else:
            value = str(value)
        if unit:
            return f"{value} {unit}"
        return value

    def _log(self, name: str, message: str, color: str = 'w'):
        self._log_row([self._timestamp(), name, message], color)

    def _timestamp(self) -> str:
        return f"{time.time() - self.start_time:07.3f}"
    
    def _log_header(self):
        self._log_row(["Time", "Step", "Result", "Criteria"])
        self._log_row(["-" * (c-1) for c in COLUMNS])

    def _log_row(self, items: list[str], color: str = 'w', temporary: bool = False):
        line = []
        for i, width in enumerate(COLUMNS):
            item = items[i] if i < len(items) else ""
            line.append(item.ljust(width))

        color = {
            "r": "\033[31m",
            "g": "\033[32m",
            "y": "\033[33m",
            "b": "\033[34m",
            "m": "\033[35m",
            "c": "\033[36m",
            "w": "\033[0m",
        }[color]

        line = color + "| " + "| ".join(line) + "|" + "\33[0m"

        if temporary:
            print(line, end="\r", flush=True)
        else:
            print(line)

