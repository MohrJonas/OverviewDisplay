class RotatingInt:
    def __init__(self, min: int, max: int) -> None:
        self.min = min
        self.max = max
        self.current = min

    def increment(self) -> None:
        self.current += 1
        if self.current > self.max:
            self.current = self.min

    def decrement(self) -> None:
        self.current -= 1
        if self.current < self.min:
            self.current = self.max
