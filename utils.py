import time


class Timer:
    time = time.perf_counter

    def __init__(self) -> None:
        self.start_time = None

    def start(self) -> None:
        self.start_time = self.time()
        self.running = True

    def _update(self) -> None:
        if self.running:
            self._elapsed_time = self.time() - self.start_time

    def stop(self) -> None:
        self._update()
        self.running = False

    @property
    def elapsed_time(self) -> float:
        self._update()
        return self._elapsed_time
