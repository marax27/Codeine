from threading import Event, Thread
from abc import ABC, abstractmethod


class StoppableThread(Thread, ABC):
    def __init__(self):
        super().__init__()
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def requested_stop(self) -> bool:
        return self._stop_event.is_set()

    @abstractmethod
    def run(self):
        pass
    
