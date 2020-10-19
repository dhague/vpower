from configparser import ConfigParser

import sys
from ant.core import log
from BtAtsPowerCalculator import BtAtsPowerCalculator
from KurtKineticPowerCalculator import KurtKineticPowerCalculator
from TacxBlueMotionPowerCalculator import TacxBlueMotionPowerCalculator
from constants import *
import hashlib

VPOWER_DEBUG = True

CONFIG = ConfigParser()
_CONFIG_FILENAME = 'vpower.cfg'
# If there's a command-line argument, it's the location of the config file
if len(sys.argv) > 1:
    _CONFIG_FILENAME = sys.argv[1]

SECTION = 'vpower'

try:
    if VPOWER_DEBUG:
        print('Open file ' + _CONFIG_FILENAME)
        print('Parse config')
    CONFIG.read(_CONFIG_FILENAME)
except Exception as e:
    print("Error: "+repr(e.__class__))

if VPOWER_DEBUG: print('Get config items')

# Type of sensor connected to the trainer
SENSOR_TYPE = CONFIG.getint(SECTION, 'speed_sensor_type')

# ANT+ ID of the above sensor
SPEED_SENSOR_ID = CONFIG.getint(SECTION, 'speed_sensor_id')

# Calculator for the model of turbo
pc_class = globals()[CONFIG.get(SECTION, 'power_calculator')]
POWER_CALCULATOR = pc_class()

# For wind/air trainers, current air density in kg/m3 (if not using a BME280 weather sensor)
POWER_CALCULATOR.air_density = CONFIG.getfloat(SECTION, 'air_density')

# For wind/air trainers, how often (secs) to update the air density if there *is* a BME280 present
POWER_CALCULATOR.air_density_update_secs = CONFIG.getfloat(SECTION, 'air_density_update_secs')

# For tyre-driven trainers, the wheel circumference in meters (2.122 for Continental Home trainer tyre)
POWER_CALCULATOR.wheel_circumference = CONFIG.getfloat(SECTION, 'wheel_circumference')

# Overall correction factor, e.g. to match a user's power meter on another bike
POWER_CALCULATOR.set_correction_factor(CONFIG.getfloat(SECTION, 'correction_factor'))

# ANT+ ID of the virtual power sensor
# The expression below will choose a fixed ID based on the CPU's serial number
POWER_SENSOR_ID = int(int(hashlib.md5(getserial().encode()).hexdigest(), 16) & 0xfffe) + 1

# If set to True, the stick's driver will dump everything it reads/writes from/to the stick.
DEBUG = CONFIG.getboolean(SECTION, 'debug')

POWER_CALCULATOR.set_debug(DEBUG or VPOWER_DEBUG)

# Set to None to disable ANT+ message logging
LOG = None
# LOG = log.LogWriter(filename="vpower.log")

# ANT+ network key
NETKEY = b'\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

if LOG:
    print("Using log file:", LOG.filename)
    print("")
