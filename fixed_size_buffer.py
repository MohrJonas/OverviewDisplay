from typing import TypeVar, Generic

T = TypeVar("T")


class FixedSizeBuffer(Generic[T]):
    def __init__(self, size: int) -> None:
        self.size = size
        self.__data: list[T] = []

    def append(self, element: T) -> None:
        self.__data.append(element)
        if len(self.__data) >= self.size:
            self.__data = self.__data[-(self.size) : :]

    def as_list(self) -> list[T]:
        return self.__data
