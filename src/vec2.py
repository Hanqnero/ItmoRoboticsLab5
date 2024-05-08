import math
from typing import Self

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = self.atan2()

    def norm(self) -> float:
        return self.x*self.x+self.y*self.y

    def atan2(self):
        return math.atan2(self.y, self.x)

    def __sub__(self, other: Self) -> Self:
        return Vec2(self.x-other.x, self.y-other.y)

    def __add__(self, other: Self) -> Self:
        return Vec2(self.x+other.x, self.y-other.y)
