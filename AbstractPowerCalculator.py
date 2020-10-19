import time


class AbstractPowerCalculator(object):
    def __init__(self):
        self.power = 0.0
        self.energy = 0.0
        self.init_time = time.time()
        self.last_time = self.init_time
        self.observer = None  # callback method
        self.correction_factor = 1.0  # default value - can be overridden in config.py

    _DEBUG = False  # default value - can be overridden in config.py

    def power_from_speed(self, revs_per_sec):
        raise NotImplemented  # This should be implemented in the subclass

    def notify_change(self, observer):
        self.observer = observer

    def set_correction_factor(self, correction_factor):
        self.correction_factor = correction_factor

    @staticmethod
    def set_debug(debug):
        AbstractPowerCalculator._DEBUG = debug

    def update(self, revs_per_sec):
        power = self.power_from_speed(revs_per_sec)
        current_time = time.time()
        time_gap = (current_time - self.last_time)
        delta_energy = power * time_gap

        # We just keep track of energy and time for now
        self.energy += delta_energy
        self.last_time = current_time
        if self._DEBUG: print("cumulative_time(): " + repr(self.cumulative_time()))

        # We only update the observer with a power reading up to twice a second, which is roughly
        # as often as a crank-based power meter
        if self.cumulative_time() > 0.5:
            self.send_power()

    def cumulative_time(self):
        return self.last_time - self.init_time

    def send_power(self):
        if self._DEBUG: print("send_power")
        timeGap = self.cumulative_time()
        if timeGap == 0.0:
            return

        # Calculate power as energy/time
        avePower = self.energy / timeGap
        # Reinitialise cumulative time & energy
        self.init_time = self.last_time
        self.energy = 0.0

        # Tell whoever is listening
        if self.observer:
            self.observer.update(avePower)
            if self._DEBUG: print("Power: ", repr(avePower))
        else:
            print("Power: ", repr(avePower))
