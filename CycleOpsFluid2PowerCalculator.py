from AbstractPowerCalculator import AbstractPowerCalculator


'''
Linear interpolation. Numpy could be used here,
but the app should be kept thin
'''
def interp(x_arr, y_arr, x):
    for i, xi in enumerate(x_arr):
        if xi >= x:
            break
    else:
        return 611

    x_min = x_arr[i - 1]
    y_min = y_arr[i - 1]
    y_max = y_arr[i]
    factor = (x - x_min) / (xi - x_min)
    return y_min + (y_max - y_min) * factor


'''
CycleOps Fluid2 power calculator.
'''
class CycleOpsFluid2PowerCalculator(AbstractPowerCalculator):
    def __init__(self):
        super(CycleOpsFluid2PowerCalculator, self).__init__()
        self.wheel_circumference = 2.105  # default value - can be overridden in config.py

    # Data from the diagram of CycleOps Fluid2:
    # http://thebikegeek.blogspot.com/2009/12/while-we-wait-for-better-and-better.html
    # speed values
    xp = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
    # power values
    yp = [0.0, 28.0, 58.0, 92.0, 132.0, 179.0, 237.0, 307.0, 391.0, 492.0, 611.0]

    def power_from_speed(self, revs_per_sec):
        kms_per_rev = self.wheel_circumference / 1000.0
        speed = revs_per_sec * 3600 * kms_per_rev
        power = int(interp(self.xp, self.yp, speed))
        return power

    def set_wheel_circumference(self, circumference):
        self.wheel_circumference = circumference


