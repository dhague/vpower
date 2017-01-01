import time
import math
import sys

from config import AIR_DENSITY, CORRECTION_FACTOR, DEBUG


class BtAtsPowerCalculator(object):
    def __init__(self):
        self.power = 0.0
        self.energy = 0.0
        self.init_time = time.time()
        self.last_time = self.init_time
        self.observer = None  # callback method
        self.air_density_correction = 0.0
        # 1.191 is the air density at which the coefficients above were determined
        self.default_air_density = self.air_density = 1.191

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
        if DEBUG: print "power_from_speed"
        if self.air_density_correction == 0.0:
            self.update_air_density_correction()
        if DEBUG: print "air_density_correction: "+repr(self.air_density_correction)
        rs = revs_per_sec
        power = self.air_density_correction * (self.A * rs * rs * rs +
                                               self.B * rs * rs +
                                               self.C * rs +
                                               self.D)

        current_time = time.time()
        time_gap = (current_time - self.last_time)
        delta_energy = power * time_gap
        self.energy += delta_energy
        self.last_time = current_time
        if DEBUG: print "cumulative_time(): "+repr(self.cumulative_time())
        if self.cumulative_time() > 0.5:
            self.get_ave_power()

    def update_air_density_correction(self):
        self.air_density_correction = CORRECTION_FACTOR * self.air_density / self.default_air_density

    @staticmethod
    def calc_air_density(t, p, h):
        if DEBUG: print "set_air_density(temp="+repr(t)+", press="+repr(p)+", humi="+repr(h)+")"
        Rd = 287.05   # Specific gas constant for dry air J / (KgK)
        Rv = 461.495  # Specific gas constant for water vapour J / (KgK)
        water_vapour_pressure = BtAtsPowerCalculator.saturation_pressure(t) * h / 100.0
        if DEBUG: print("water_vapour_pressure: ", water_vapour_pressure)
        dry_air_pressure = (p*100.0) - water_vapour_pressure
        if DEBUG: print("dry_air_pressure: ", dry_air_pressure)
        temperatureK = t + 273.15
        if DEBUG: print("temperatureK: ", temperatureK)
        return ((dry_air_pressure / (Rd * temperatureK)) + (water_vapour_pressure / (Rv * temperatureK)))

    def update_air_density(self, t, p, h):
        self.air_density = self.calc_air_density(t, p, h)
        if DEBUG: print("air density: ", self.air_density)
        self.update_air_density_correction()
        sys.stdout.write('o')
        sys.stdout.flush()

    @staticmethod
    def saturation_pressure(t):
        Eso = 6.1078 * 100 # * 100 for Pa instead of hPa
        c0 = 0.99999683
        c1 = -0.90826951e-2
        c2 = 0.78736169e-4
        c3 = -0.61117958e-6
        c4 = 0.43884187e-8
        c5 = -0.29883885e-10
        c6 = 0.21874425e-12
        c7 = -0.17892321e-14
        c8 = 0.11112018e-16
        c9 = -0.30994571e-19
        p = (c0 + t * (c1 + t * (c2 + t * (c3 + t * (c4 + t * (c5 + t * (c6 + t * (c7 + t * (c8 + t * (c9))))))))))
        return Eso / math.pow(p, 8)

    def update(self, revs_per_sec):
        self.power_from_speed(revs_per_sec)

    def cumulative_time(self):
        return self.last_time - self.init_time

    def get_ave_power(self):
        if DEBUG: print "get_ave_power"
        timeGap = self.cumulative_time()
        avePower = 0.0
        if timeGap != 0.0:
            avePower = self.energy / timeGap

        self.init_time = self.last_time
        self.energy = 0.0
        if self.observer:
            self.observer.update(avePower)
            if DEBUG: print "Power: ", repr(avePower)
        else:
            print "Power: ", repr(avePower)
        return avePower
