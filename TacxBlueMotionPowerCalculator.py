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
        return 560

    x_min = x_arr[i - 1]
    y_min = y_arr[i - 1]
    y_max = y_arr[i]
    factor = (x - x_min) / (xi - x_min)
    return y_min + (y_max - y_min) * factor


'''
Tacx Blue Motion power calculator. Uses fixed lever position 4.
'''
class TacxBlueMotionPowerCalculator(AbstractPowerCalculator):
    def __init__(self):
        super(TacxBlueMotionPowerCalculator, self).__init__()
        self.wheel_circumference = 2.122  # default value - can be overridden in config.py

    # Data from the diagram of Tacx Blue Motion 4/10:
    # http://www.powercurvesensor.com/cycling-trainer-power-curves/
    # speed values
    xp = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0,
          30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0]
    # power values
    yp = [0.0, 33.0, 65.0, 100.0, 135.0, 175.0,
          217.0, 260.0, 308.0, 364.0, 424.0, 488.0, 560.0]

    def power_from_speed(self, revs_per_sec):
        kms_per_rev = self.wheel_circumference / 1000.0
        speed = revs_per_sec * 3600 * kms_per_rev
        power = int(interp(self.xp, self.yp, speed))
        return power

    def set_wheel_circumference(self, circumference):
        self.wheel_circumference = circumference


