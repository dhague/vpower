import math
import sys
import time

from AbstractPowerCalculator import AbstractPowerCalculator


class BtAtsPowerCalculator(AbstractPowerCalculator):
    def __init__(self):
        super(BtAtsPowerCalculator, self).__init__()
        # 1.191 is the air density at which the coefficients above were determined
        self.air_density_timer = time.time()
        self.air_density_update_secs = 10
        self.default_air_density = self.air_density = 1.191
        self.air_density_correction = 0.0
        self.update_air_density_correction()
        self.dynamic_air_density = None

    def check_for_bme280_sensor(self):
        print("Check for temperature/pressure/humidity sensor")
        try:
            import os, sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            # import ../bme280.py
            import bme280
            bme280.readBME280All()  # The first reading after boot-up can be off, so throw it away
            temperature, pressure, humidity = bme280.readBME280All()
            print("Temp (C): " + repr(temperature))
            print("Pressure: " + repr(pressure))
            print("Humidity: " + repr(humidity))
            print("Air density: " + repr(self.calc_air_density(temperature, pressure, humidity)))
            self.dynamic_air_density = True
        except (ImportError, IOError) as e:
            self.dynamic_air_density = False
            print("Not found")

    A = 0.290390167
    B = -0.0461311774
    C = 0.592125507
    D = 0.0

    # from Steven Sansonetti of Bike Technologies:
    # This is a 3rd order polynomial, where
    #  Power = A * v ^ 3 + B * v ^ 2 + C * v + d
    # where v is speed in revs / sec and constants A, B, C & D are as defined above.
    def power_from_speed(self, revs_per_sec):
        if self._DEBUG: print("power_from_speed")

        if self.dynamic_air_density is None:
            self.check_for_bme280_sensor()

        if self.dynamic_air_density and (time.time() - self.air_density_timer > self.air_density_update_secs):
            self.air_density_timer = time.time()
            import bme280
            temperature, pressure, humidity = bme280.readBME280All()
            if self._DEBUG:
                print("Temp (C): " + repr(temperature))
                print("Pressure: " + repr(pressure))
                print("Humidity: " + repr(humidity))
            self.update_air_density(temperature, pressure, humidity)

        if self._DEBUG: print("air_density_correction: " + repr(self.air_density_correction))
        rs = revs_per_sec
        power = self.correction_factor * (self.A * rs * rs * rs * self.air_density_correction +
                                          self.B * rs * rs +
                                          self.C * rs +
                                          self.D)
        return power

    def update_air_density_correction(self):
        self.air_density_correction = self.air_density / self.default_air_density

    @staticmethod
    def calc_air_density(t, p, h):
        _DEBUG = BtAtsPowerCalculator._DEBUG
        if _DEBUG: print("set_air_density(temp=" + repr(t) + ", press=" + repr(p) + ", humi=" + repr(h) + ")")
        Rd = 287.05  # Specific gas constant for dry air J / (KgK)
        Rv = 461.495  # Specific gas constant for water vapour J / (KgK)
        water_vapour_pressure = BtAtsPowerCalculator.saturation_pressure(t) * h / 100.0
        if _DEBUG: print("water_vapour_pressure: ", water_vapour_pressure)
        dry_air_pressure = (p * 100.0) - water_vapour_pressure
        if _DEBUG: print("dry_air_pressure: ", dry_air_pressure)
        temperatureK = t + 273.15
        if _DEBUG: print("temperatureK: ", temperatureK)
        return (dry_air_pressure / (Rd * temperatureK)) + (water_vapour_pressure / (Rv * temperatureK))

    def update_air_density(self, t, p, h):
        self.air_density = self.calc_air_density(t, p, h)
        if self._DEBUG: print("air density: ", self.air_density)
        self.update_air_density_correction()
        sys.stdout.write('o')
        sys.stdout.flush()

    @staticmethod
    def saturation_pressure(t):
        # Estimation algorithm due to Herman Wobus (see https://wahiduddin.net/calc/density_altitude.htm)
        Eso = 6.1078 * 100  # * 100 for Pa instead of hPa
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
        p = (c0 + t * (c1 + t * (c2 + t * (c3 + t * (c4 + t * (c5 + t * (c6 + t * (c7 + t * (c8 + t * c9)))))))))
        return Eso / math.pow(p, 8)
