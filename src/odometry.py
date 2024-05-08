class Integral:
    def __init__(self, initial_value, x0, dt):
       self.value = initial_value
       self.last_measure = x0
       self.dt = dt

    def add_measure(self, measure):
        self.value += (self.last_measure + measure)*self.dt / 2
        self.last_measure = measure
