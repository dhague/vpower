from ant.core import log
from BtAtsPowerCalculator import BtAtsPowerCalculator
from KurtKineticPowerCalculator import KurtKineticPowerCalculator
from constants import *
import hashlib

# Type of sensor connected to the trainer
# SENSOR_TYPE = SPEED_DEVICE_TYPE
# SENSOR_TYPE = CADENCE_DEVICE_TYPE
SENSOR_TYPE = SPEED_CADENCE_DEVICE_TYPE

# ANT+ ID of the above sensor
SPEED_SENSOR_ID = 24090

# Uncomment for the model of turbo you are using
POWER_CALCULATOR = BtAtsPowerCalculator()
# POWER_CALCULATOR = KurtKineticPowerCalculator()

# For wind/air trainers, current air density in kg/m3 (if not using a BME280 weather sensor)
#  Hint: there's an online calculator at http://barani.biz/apps/air-density/ to help you work it out,
#        or you can use the one built into Golden Cheetah
POWER_CALCULATOR.air_density = 1.191

# For wind/air trainers, how often (secs) to update the air density if there is a BME280 present
POWER_CALCULATOR.air_density_update_secs = 10

# For tyre-driven trainers, the wheel circumference in meters (2.122 for Continental Home trainer tyre)
POWER_CALCULATOR.wheel_circumference = 2.122

# Overall correction factor, e.g. to match a user's power meter on another bike
# POWER_CALCULATOR.set_correction_factor(0.949)
POWER_CALCULATOR.set_correction_factor(1.0)

# ANT+ ID of the virtual power sensor
# The expression below will choose a fixed ID based on the CPU's serial number
POWER_SENSOR_ID = int(int(hashlib.md5(getserial()).hexdigest(), 16) & 0xfffe) + 1
# POWER_SENSOR_ID = 22222
print "Power meter ANT+ ID: " + repr(POWER_SENSOR_ID)

# If set to True, the stick's driver will dump everything it reads/writes
# from/to the stick.
# Some demos depend on this setting being True, so unless you know what you
# are doing, leave it as is.
DEBUG = False
POWER_CALCULATOR.set_debug(DEBUG)

# Set to None to disable logging
LOG = None
# LOG = log.LogWriter(filename="vpower.log")

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

if LOG:
    print "Using log file:", LOG.filename
    print ""
