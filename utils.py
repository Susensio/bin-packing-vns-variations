import time
import contextlib
import errno
import os
import signal
from math import ceil

import logs

DEFAULT_TIMEOUT_MESSAGE = os.strerror(errno.ETIME)


@logs.append_logger
class Timer:
    time = time.perf_counter

    def __init__(self) -> None:
        self.start_time = None
        self.running = False

    def start(self) -> None:
        if not self.running:
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

    @contextlib.contextmanager
    def timeout(self, seconds, *,
                suppress_timeout_errors=True):
        """ Inspired by https://gist.github.com/TySkby/143190ad1b88c6115597c45f996b030c """
        self.start()

        def _timeout_handler(signum, frame):
            raise TimeoutError(DEFAULT_TIMEOUT_MESSAGE)

        signal.signal(signal.SIGALRM, _timeout_handler)
        remaining = seconds-self.elapsed_time
        signal.alarm(ceil(remaining))

        try:
            yield
        except TimeoutError as exc:
            if not suppress_timeout_errors:
                raise exc
        finally:
            signal.alarm(0)


if __name__ == "__main__":
    t = Timer()
    with t.timeout(2):
        print("start")
        time.sleep(3)
        print("end")
    print("finally")
