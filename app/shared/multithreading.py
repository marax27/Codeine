from threading import Event, Thread


class StoppableThread(Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def requested_stop(self) -> bool:
        return self._stop_event.is_set()
