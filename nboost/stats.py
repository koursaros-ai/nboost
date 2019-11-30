from typing import Callable, Union
import functools
import time

NUMBER = Union[int, float]


class ClassStatistics:
    """A helper class for storing the statistics for a class. Should be bound
    to the class. Time contexts and variable contexts are added to the
    statistics record when the decorated function is called."""
    def __init__(self):
        self.record = {'time': {}, 'vars': {}}

    @staticmethod
    def mean(previous_avg: NUMBER, new_value: NUMBER, calls: NUMBER) -> float:
        """Rolling average"""
        return (previous_avg * calls + new_value) / (calls + 1)

    def record_rolling_avg(self, record: dict, new_value: NUMBER):
        """Update a given record with a new value"""
        avg, calls = record['avg'], record['calls']
        new_avg = self.mean(avg, new_value, calls)
        record['calls'] += 1
        record['avg'] = new_avg

    def record_time(self, func_name: str, ms_elapsed: float):
        """Update the function average time"""
        if func_name not in self.record['time']:
            self.record['time'][func_name] = dict(avg=0, calls=0)

        time_record = self.record['time'][func_name]
        self.record_rolling_avg(time_record, ms_elapsed)

    def record_var(self, var_name: str, value: Union[int, list]):
        """Add a number to the number record for that variable. The number
        recorded depends on the variable type:

            int/float: avg value
            list: avg length of list
        """
        if var_name not in self.record['vars']:
            self.record['vars'][var_name] = dict(avg=0, calls=0, type=[])

        var_record = self.record['vars'][var_name]
        var_record['type'] = set(var_record['type'])
        var_record['type'].add(value.__class__.__name__)
        var_record['type'] = list(var_record['type'])

        if isinstance(value, (int, float)):
            self.record_rolling_avg(var_record, value)
        elif isinstance(value, list):
            self.record_rolling_avg(var_record, len(value))

    def time_context(self, func: Callable):
        """Records the time within a func context and stores the latency (ms)
         within a record (dict)"""
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            """Decorator for function with a timed context"""
            start = time.perf_counter()
            ret = func(*args, **kwargs)
            ms_elapsed = (time.perf_counter() - start) * 1000
            self.record_time(func.__name__, ms_elapsed)
            return ret
        return decorator

    def vars_context(self, func: Callable):
        """Records the variable with a value depending on it's type. See
        time_context() for more info."""
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            """Decorator for function with a var context"""
            for var, value in kwargs.items():
                self.record_var(var, value)
            ret = func(*args, **kwargs)
            return ret

        return decorator
