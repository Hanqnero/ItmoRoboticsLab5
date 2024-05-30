import math


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = self.atan2()

    def norm(self) -> float:
        return self.x * self.x + self.y * self.y

    def atan2(self):
        return math.atan2(self.y, self.x)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y - other.y)

    def __mul__(self, other):
        return self.x * other.x + self.y * other.y


def shift_angle(x):
    """
    Возвращает идентичный угол в пределах [-pi; pi]
    :param x: Угол в радианах
    :return: Идентичный угол в пределах [-pi; pi]
    """
    direction = 2 if x >= 0 else -2
    r = x
    while math.fabs(r) > math.pi:
        r -= direction * math.pi
    return r
