import unittest
from TacxBlueMotionPowerCalculator import TacxBlueMotionPowerCalculator


class TacxBlueMotionPowerCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.calculator = TacxBlueMotionPowerCalculator()

    def test_calculation_min(self):
        power = self.calculator.power_from_speed(0.0)
        self.assertEqual(power, 0)

    def test_calculation_1(self):
        power = self.calculator.power_from_speed(self.get_revs(9.7))
        self.assertEqual(power, 63)

    def test_calculation_2(self):
        power = self.calculator.power_from_speed(self.get_revs(16.3))
        self.assertEqual(power, 109)

    def test_calculation_3(self):
        power = self.calculator.power_from_speed(self.get_revs(42.1))
        self.assertEqual(power, 331)

    def test_calculation_max(self):
        power = self.calculator.power_from_speed(self.get_revs(88.1))
        self.assertEqual(power, 560)

    def get_revs(self, speed_kph):
        speed_mps = speed_kph / 3.6
        return speed_mps / self.calculator.wheel_circumference
