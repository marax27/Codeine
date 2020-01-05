from time import time


class TimeoutService:
    def __init__(self, timeout_threshold: float):
        self._timeout_threshold = timeout_threshold

    def timed_out(self, time_value: float) -> bool:
        return self.now() - time_value >= self._timeout_threshold

    def now(self) -> float:
        return time()
