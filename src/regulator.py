class Regulator:
    """Regulator interface defining signature of main method __call__"""
    def __call__(self, error: float) -> float:
        pass

class PRegulator(Regulator):
    def __call__(self, error: float) -> float:
        return self.kp * error

    def __init__(self, kp: float):
        self.kp = kp
