from AbstractPowerCalculator import AbstractPowerCalculator
from LinearInterpolationPowerCalculator import interp


'''
Elite Novo Force 3/8 power calculator. Thanks @MichMarrazzo
'''
class EliteNovoForcePowerCalculator(AbstractPowerCalculator):
    def __init__(self):
        super(EliteNovoForcePowerCalculator, self).__init__()
        self.wheel_circumference = 2.105  # default value - can be overridden in config.py

    # Data from Elite (3/8):
    # http://www.powercurvesensor.com/cycling-trainer-power-curves/
    # http://velocompforum.com/download/file.php?id=4208&sid=fba82c0db53a42bf4292612df4f28c15
    # Missing data grabbed from Elite app, which seems to match the provided data
    # speed values
    xp = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0]
    # power values
    yp = [0.0, 11.0, 43.0, 74.0, 108.0, 146.0, 184.0, 225.0, 267.0, 310.0, 356.0, 405.0, 441.0]

    def power_from_speed(self, revs_per_sec):
        kms_per_rev = self.wheel_circumference / 1000.0
        speed = revs_per_sec * 3600 * kms_per_rev
        power = int(interp(self.xp, self.yp, speed))
        return power

    def set_wheel_circumference(self, circumference):
        self.wheel_circumference = circumference
