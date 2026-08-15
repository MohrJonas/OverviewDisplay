from typing import TypeVar, Callable
from fixed_size_buffer import FixedSizeBuffer

T = TypeVar("T")


class ChartPage:
    def __init__(
        self, title: str, data_acquirere: Callable[[], int], update_delay: int
    ) -> None:
        self.dirty = False
        self.title = title
        self.data_acquirere = data_acquirere
        self.update_delay = update_delay
        self.data: FixedSizeBuffer[int] = FixedSizeBuffer(200)


class TablePage:
    def __init__(
        self, data_acquirere: Callable[[], list[tuple[str, str]]], update_delay: int
    ) -> None:
        self.dirty = False
        self.data_acquirere = data_acquirere
        self.update_delay = update_delay
        self.data: list[tuple[str, str]] = []
