from typing import Callable, TypeVar
import re, time, datetime


T = TypeVar("T")


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
        self._log("Test start", ts)

    def stop(self):
        if self.running:
            self.running = False

            if self.passed_tests:
                self._log("PASS", f"{self.passed_tests} / {self.total_tests} tests passed", 'g')
            else:
                self._log("FAIL", f"{self.passed_tests} / {self.total_tests} tests passed", 'r')

    def test(self, name: str, func: Callable[[],bool]) -> bool:
        predicate = lambda x: x
        return self._test_internal(name, func, predicate, None, None)

    def test_within(self, name: str, func: Callable[[], T], min: T = None, max: T = None, unit: str = None) -> bool:
        predicate = lambda x: (min == None or x >= min) and (max == None or x <= max)
        condition = ("" if min == None else f"{self._format_value(min, unit)} <= ") + "x" + ("" if max == None else f" >= {self._format_value(max, unit)}")
        return self._test_internal(name, func, predicate, condition, unit)

    def test_equal(self, name: str, func: Callable[[],T], expected: T, unit: str = None) -> bool:
        predicate = lambda x: x == expected
        condition = f"x == {self._format_value(expected, unit)}"
        return self._test_internal(name, func, predicate, condition, unit)

    def test_pattern(self, name: str, func: Callable[[], str], pattern: str) -> bool:
        predicate = lambda x: re.match(pattern, x) != None
        condition = f"pattern matches \"{pattern}\""
        return self._test_internal(name, func, predicate, condition, None)
    
    def test_log(self, name: str, func: Callable[[], T], unit: str = None) -> bool:
        predicate = lambda x: True
        return self._test_internal(name, func, predicate, unit)

    def _test_internal(self, name: str, func: Callable[[], T], predicate: Callable[[T],bool], condition: str, unit: str) -> bool:

        self.total_tests += 1
        if not self.running:
            return False
        
        self._pre_log(name)
        try:
            result = func()
            passed = predicate(result)
        except Exception as e:
            self._log_result(name, "Exception occurred, {e}")
            return False

        if passed:
            self.passed_tests += 1
        self._log_result(name, self._format_value(result, unit), condition, color=('w' if passed else 'r'))
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
    
    def _pre_log(self, name: str):
        print(f"[       ] {name}: ...", end="\r", flush=True)

    def _log_result(self, name: str, message: str, condition: str = None, color: str = 'w'):
        color = {
            "r": "\033[31m",
            "g": "\033[32m",
            "y": "\033[33m",
            "b": "\033[34m",
            "m": "\033[35m",
            "c": "\033[36m",
            "w": "\033[0m",
        }[color]
        elapsed = time.time() - self.start_time

        body = f"{name}: {message}" if message != None else name
        if condition:
            body = f"{body} ({condition})"
        print(f"\033[K{color}[{elapsed:07.3f}] {body}\33[0m")

    def _log(self, name: str, message: str = None, color: str = 'w'):
        self._log_result(name, message, color=color)