import time

from config import AIR_DENSITY, CORRECTION_FACTOR, DEBUG


class BtAtsPowerCalculator(object):
    def __init__(self):

        self.power = 0.0
        self.energy = 0.0
        self.initTime = time.time()
        self.lastTime = self.initTime
        self.observer = None  # callback method
        self.airDensityCorrection = 0.0
        # 1.191 is the air density at which the coefficients above were determined
        self.defaultAirDensity = 1.191

    def notify_change(self, observer):
        self.observer = observer

    A = 0.290390167
    B = -0.0461311774
    C = 0.592125507
    D = 0.0

    # from Steven Sansonetti of Bike Technologies:
    # This is a 3rd order polynomial, where
    #  Power = A * v ^ 3 + B * v ^ 2 + C * v + d
    # where v is speed in revs / sec and constants A, B, C & D are as defined above.
    def power_from_speed(self, revs_per_sec):
        if DEBUG:
            print "powerFromSpeed"
        if self.airDensityCorrection == 0.0:
            self.update_air_density_correction()
        rs = revs_per_sec
        power = self.airDensityCorrection * (self.A * rs * rs * rs +
                                             self.B * rs * rs +
                                             self.C * rs +
                                             self.D)

        current_time = time.time()
        timeGap = (current_time - self.lastTime)
        deltaEnergy = power * timeGap
        self.energy += deltaEnergy
        self.lastTime = current_time
        if self.cumulative_time() > 0.5:
            self.get_ave_power()

    def update_air_density_correction(self):
        self.airDensityCorrection = CORRECTION_FACTOR * AIR_DENSITY / self.defaultAirDensity

    def update(self, revs_per_sec):
        self.power_from_speed(revs_per_sec)

    def cumulative_time(self):
        return self.lastTime - self.initTime

    def get_ave_power(self):
        if DEBUG: print "get_ave_power"
        timeGap = self.cumulative_time()
        avePower = 0.0
        if timeGap != 0.0:
            avePower = self.energy / timeGap

        self.initTime = self.lastTime
        self.energy = 0.0
        if self.observer:
            self.observer.update(avePower)
        else:
            print "Power: ", avePower
        return avePower
