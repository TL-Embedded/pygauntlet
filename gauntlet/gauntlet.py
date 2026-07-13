from typing import Callable
import time, datetime

from .criteria import *
from .util import T, format_value, console_color, free_filename


COLUMNS = [8, 28, 28, 6, 28, 8]
HEADERS = ["Time", "Step", "Result", "Unit", "Criteria", "Status"]


class Gauntlet():
    
    def __init__(self, name: str = "", path: str = None):
        self.name = name
        self.running = False
        self.result_path = path
        self.file = None

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

        if self.result_path != None:
            self.result_path = free_filename(self.result_path, ".md")
            self.file = open(self.result_path, 'w')

        self._log_header()
        self._log(name="Test start", result=ts)

    def stop(self):
        if self.running:
            self.running = False

            if self.passed_tests == self.total_tests:
                self._log(name="Test passed", result=f"{self.passed_tests} / {self.total_tests} tests passed", status="PASS", color='g')
            else:
                self._log(name="Test failed", result=f"{self.passed_tests} / {self.total_tests} tests passed", status="FAIL", color='r')

            if self.file:
                self.file.close()

    def test(self, name: str, func: Callable[[], T]|T, unit: str = None, equal: T = None, minimum: T = None, maximum: T = None, pattern: str = None):
        
        checks = []
        if equal != None:
            checks.append(EqualsCriteria(equal))
        if minimum != None or maximum != None:
            checks.append(RangeCriteria(minimum, maximum))
        if pattern != None:
            checks.append(PatternCriteria(pattern))

        if len(checks) == 0:
            criteria = NotFalseCriteria()
        elif len(checks) == 1:
            criteria = checks[0]
        else:
            criteria = GroupCriteria(checks)

        return self.test_custom(name, func, unit, criteria)

    def test_custom(self, name: str, func: Callable[[], T]|T, unit: str, criteria: Criteria) -> bool:
        
        self.total_tests += 1
        if not self.running:
            return False
        
        if callable(func):
            self._log(name=name, unit=unit, temporary=True)
            try:
                result = func()
                passed = criteria.predicate(result)
            except Exception as e:
                self._log(name=name, result=f"Exception occured, {e}", unit=unit, criteria=criteria.describe(), color='r')
                return False
        else:
            result = func
        
        passed = criteria.predicate(result)

        if passed:
            self.passed_tests += 1

        self._log(name=name, result=format_value(result), unit=unit, criteria=criteria.describe(),
            status=("PASS" if passed else "FAIL"),
            color=('w' if passed else 'r')
            )
        return passed
    
    def _log(self, name: str, result: str = None, unit: str = None, criteria: str = None, status: str = None, color: str = 'w', temporary: bool = False):
        self._log_row([self._timestamp(), name, result, unit, criteria, status], color=color, temporary=temporary)

    def _timestamp(self) -> str:
        return f"{time.time() - self.start_time:07.3f}"
    
    def _log_header(self):
        self._log_row(HEADERS)
        self._log_row(["-" * (c-1) for c in COLUMNS])

    def _log_row(self, items: list[str], color: str = 'w', temporary: bool = False):
        line = []
        for i, width in enumerate(COLUMNS):
            item = (items[i] or "") if i < len(items) else ""
            line.append(item.ljust(width))

        text = "| " + "| ".join(line) + "|"

        line = console_color(color) + text + console_color('w')

        if temporary:
            print(line, end="\r", flush=True)
        else:
            print(line)
            if self.file:
                self.file.write(text + "\n")

