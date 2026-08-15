from threading import Thread, Event
from typing import Callable


class DisplayTimeoutThread(Thread):
    def __init__(
        self,
        timeout: int,
        on_timeout: Callable[[], None],
        on_wakeup: Callable[[], None],
    ):
        super().__init__(target=self.__run, daemon=True)
        self.timeout = timeout
        self.on_timeout = on_timeout
        self.on_wakeup = on_wakeup
        self.__sleep_event = Event()
        self.__start_event = Event()
        self.is_sleeping = False

    def __run(self) -> None:
        while True:
            print("Waiting for start event to set")
            self.__start_event.wait()
            print("Waiting for sleep event")
            was_cancelled = self.__sleep_event.wait(self.timeout)
            if was_cancelled:
                print("Sleep event was cancelled")
            else:
                print("Sleep event expired, running associated action")
                self.on_timeout()
                print("Clearing start event")
                self.__start_event.clear()
                self.is_sleeping = True
            print("Clearing sleep event")
            self.__sleep_event.clear()

    def start(self) -> None:
        self.__start_event.set()
        super().start()

    def restart(self) -> None:
        self.is_sleeping = False
        self.on_wakeup()
        self.__start_event.set()

    def cancel_timeout(self) -> None:
        self.__sleep_event.set()
