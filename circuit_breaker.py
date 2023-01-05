import datetime
import enum
import inspect
from typing import Tuple


class _CircuitState(enum.Enum):
    CLOSE = 0,
    HALF_OPEN = 1,
    OPEN = 2


class _CircuitBreaker:

    def __init__(self, max_retries: int = 10, timeout: int = 120, default_result=None, exceptions: Tuple =(BaseException,)):
        self.max_retries = max_retries
        self.timeout = timeout
        self.default_result = default_result
        self.state = _CircuitState.CLOSE
        self.exceptions_count = 0
        self.closed_timestamp = 0
        self.exceptions = exceptions

    def execute(self, func, *args, **kwargs):
        if self.state == _CircuitState.CLOSE:
            while self.exceptions_count < self.max_retries:
                try:
                    result = func(*args, **kwargs)
                    return result
                except self.exceptions as e:
                    self.exceptions_count += 1
            self.state = _CircuitState.OPEN
            self.closed_timestamp = datetime.datetime.now().timestamp()
        if self.state == _CircuitState.OPEN:
            if datetime.datetime.now().timestamp() - self.closed_timestamp > self.timeout:
                self.state = _CircuitState.HALF_OPEN
            else:
                return self.default_result
        if self.state == _CircuitState.HALF_OPEN:
            try:
                result = func(*args, **kwargs)
                self.state = _CircuitState.CLOSE
                self.exceptions_count = 0
                return result
            except self.exceptions as e:
                self.state = _CircuitState.OPEN
                self.closed_timestamp = datetime.datetime.now()
                return self.default_result

    async def a_execute(self, func, *args, **kwargs):
        if self.state == _CircuitState.CLOSE:
            while self.exceptions_count < self.max_retries:
                try:
                    result = await func(*args, **kwargs)
                    return result
                except self.exceptions as e:
                    self.exceptions_count += 1
            self.state = _CircuitState.OPEN
            self.closed_timestamp = datetime.datetime.now().timestamp()
        if self.state == _CircuitState.OPEN:
            if datetime.datetime.now().timestamp() - self.closed_timestamp > self.timeout:
                self.state = _CircuitState.HALF_OPEN
            else:
                return self.default_result
        if self.state == _CircuitState.HALF_OPEN:
            try:
                result = await func(*args, **kwargs)
                self.state = _CircuitState.CLOSE
                self.exceptions_count = 0
                return result
            except self.exceptions as e:
                self.state = _CircuitState.OPEN
                self.closed_timestamp = datetime.datetime.now()
                return self.default_result


def circuit_breaker(max_retries: int = 10, timeout: int = 120, default_result=None, exceptions: Tuple =(BaseException,)):

    cb = _CircuitBreaker(max_retries=max_retries,
                         timeout=timeout,
                         default_result=default_result,
                         exceptions=exceptions)

    def _circuit_breaker(func):

        if inspect.iscoroutinefunction(func):
            async def inner(*args, **kwargs):
                return await cb.a_execute(func, *args, **kwargs)
        else:
            def inner(*args, **kwargs):
                return cb.execute(func, *args, **kwargs)

        return inner

    return _circuit_breaker


