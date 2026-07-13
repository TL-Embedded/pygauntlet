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

        self._log_row(HEADERS)
        self._log_row(["-" * (c-1) for c in COLUMNS])
        self._log(name="Test start", result=ts)

    def stop(self):
        self.running = False

        if self.passed_tests == self.total_tests:
            self._log(name="Test passed", result=f"{self.passed_tests} / {self.total_tests} tests passed", status="PASS", final=True)
        else:
            self._log(name="Test failed", result=f"{self.passed_tests} / {self.total_tests} tests passed", status="FAIL", final=True)

        if self.file:
            self.file.close()

    def step(self, name: str,) -> 'Gauntlet.Step':
        return Gauntlet.Step(self, name)
    
    def _log(self, name: str, result: str = None, unit: str = None, criteria: str = None, status: str = None, final: bool = False, temporary: bool = False):
        if status == "RUN":
            color = 'y'
        elif status == "FAIL":
            color = 'r'
        elif status == "PASS":
            color = 'g'
        else:
            color = 'w'
        self._log_row([self._timestamp(), name, result, unit, criteria, status], color=color, final=final, temporary=temporary)

    def _timestamp(self) -> str:
        return f"{time.time() - self.start_time:07.3f}"

    def _log_row(self, items: list[str], color: str = 'w', final: bool = False, temporary: bool = False):
        line = []
        for i, width in enumerate(COLUMNS):
            item = (items[i] or "") if i < len(items) else ""
            line.append(item.ljust(width))

        if self.file and not temporary:
            file_text = "| " + "| ".join(line) + "|" + "\n"
            self.file.write(file_text)
        
        if final:
            console_text = console_color("| " + "| ".join(line) + "|", color + 'b')
        else:
            line[5] = console_color(line[5], color)
            console_text = "| " + "| ".join(line) + "|"

        if temporary:
            print(console_text, end="\r", flush=True)
        else:
            print(console_text)
                

    def _log_test_start(self, test: 'Gauntlet.Step'):
        self._log(
            name=test.name,
            status=test.status,
            temporary=True
        )

    def _log_test(self, test: 'Gauntlet.Step'):
        self.total_tests += 1
        if test.status == "PASS":
            self.passed_tests += 1
        else:
            self.running = False
        
        self._log(
            name=test.name,
            result=format_value(test.result),
            unit=test.unit,
            criteria=test.criteria.describe(),
            status=test.status,
        )

    class Step():
        def __init__(self, host: 'Gauntlet', name: str):
            self.gauntlet = host
            self.name = name
            self.result: T = None
            self.unit: str = None
            self.status = "RUN"
            self.function = None
            self.criteria: Criteria = NullCriteria()

        def skip(self):
            self.status = "SKIP"
            self.gauntlet._log_test(self)

        def run(self) -> T:
            if not self.gauntlet.running:
                self.skip()
                return None
            
            if self.function:
                self.gauntlet._log_test_start(self)

                try:
                    self.result = self.function()
                except Exception as e:
                    self.status = "FAIL"
                    self.result = e
                    self.gauntlet._log_test(self)
                    return None
            
            passing = self.criteria.evaluate(self.result)
            self.status = "PASS" if passing else "FAIL"

            self.gauntlet._log_test(self)
            return self.result
        
        def set(self, value: T, unit: str = None) -> 'Gauntlet.Step':
            self.result = value
            self.unit = unit
            return self
        
        def method(self, function: Callable[[], T], unit: str = None) -> 'Gauntlet.Step':
            self.function = function
            self.unit = unit
            return self
        
        def equals(self, value: T) -> 'Gauntlet.Step':
            return self.add_criteria( EqualsCriteria(value) )

        def within(self, minimum: T, maximum: T) -> 'Gauntlet.Step':
            return self.add_criteria( RangeCriteria(minimum, maximum) )
        
        def minimum(self, minimum: T) -> 'Gauntlet.Step':
            return self.add_criteria( RangeCriteria(minimum=minimum) )
        
        def maximum(self, maximum: T) -> 'Gauntlet.Step':
            return self.add_criteria( RangeCriteria(maximum=maximum) )
        
        def pattern(self, pattern: str) -> 'Gauntlet.Step':
            return self.add_criteria( PatternCriteria(pattern) )

        def add_criteria(self, criteria: Criteria) -> 'Gauntlet.Step':
            if type(self.criteria) is NullCriteria:
                self.criteria = criteria
            elif type(self.criteria) is GroupCriteria:
                self.criteria.append(criteria)
            else:
                self.criteria = GroupCriteria([self.criteria, criteria])
            return self



