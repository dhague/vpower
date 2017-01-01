from ant.core import log
from constants import *
import hashlib

# Type of sensor connected to the trainer
#SENSOR_TYPE = SPEED_DEVICE_TYPE
#SENSOR_TYPE = CADENCE_DEVICE_TYPE
SENSOR_TYPE = SPEED_CADENCE_DEVICE_TYPE

# ANT+ ID of the above sensor
SPEED_SENSOR_ID = 24090

# Current air density
AIR_DENSITY = 1.191

# How often (secs) to update the air density if there is a BME280 present
AIR_DENSITY_UPDATE_SECS = 10

# Overall correction factor, e.g. to match a user's power meter on another bike
CORRECTION_FACTOR = 0.96

# ANT+ ID of the virtual power sensor
# Expression below will choose a fixed ID based on the CPU's serial number
POWER_SENSOR_ID = int(int(hashlib.md5(getserial()).hexdigest(),16)&0xfffe)+1
#POWER_SENSOR_ID = 22222
print "Power meter ANT+ ID: "+repr(POWER_SENSOR_ID)

# If set to True, the stick's driver will dump everything it reads/writes
# from/to the stick.
# Some demos depend on this setting being True, so unless you know what you
# are doing, leave it as is.
DEBUG = False

# Set to None to disable logging
LOG = None
#LOG = log.LogWriter(filename="vpower.log")

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

# ========== DO NOT CHANGE ANYTHING BELOW THIS LINE ==========
if LOG:
    print "Using log file:", LOG.filename
    print ""

