from odometry import Integral


def clamp(x, max_, min_):
    return max(min(x, max_), min_)


class Regulator:
    def __init__(self, kp: float, saturation: int, dt: float):
        self.kp = kp
        self.ki = kp * .75
        self.saturation = saturation
        self.integral = Integral(0, 0, dt)

    def clamp(self, x):
        return clamp(x, self.saturation, -self.saturation)

    def __call__(self, error: float) -> int:
        P = error * self.kp
        I = self.ki * self.integral.value

        return self.clamp(P + I)
