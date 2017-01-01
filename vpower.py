import time

# Initialize
from ant.core import driver
from ant.core import node

from BtAtsPowerCalculator import BtAtsPowerCalculator
from PowerMeterTx import PowerMeterTx
from SpeedCadenceSensorRx import SpeedCadenceSensorRx
from config import *

stick = driver.USB2Driver(SERIAL, log=LOG, debug=DEBUG)
antnode = node.Node(stick)
print "Starting ANT node"
antnode.start()
key = node.NetworkKey('N:ANT+', NETKEY)
antnode.setNetworkKey(0, key)

print "Starting speed sensor"
try:
    # Create the speed sensor object and open it
    scSensor = SpeedCadenceSensorRx(antnode)
    scSensor.open()
except Exception as e:
    print("scSensor error: "+e.getMessage())
    scSensor = None

powerCalculator = BtAtsPowerCalculator()
# Notify the power calculator every time we get a speed event
scSensor.notify_change(powerCalculator)
print "Starting power meter"
try:
    # Create the power meter object and open it
    powerMeter = PowerMeterTx(antnode)
    powerMeter.open()
except Exception as e:
    print("powerMeter error: "+e.getMessage())
    powerMeter = None

# Notify the power meter every time we get a calculated power value
powerCalculator.notify_change(powerMeter)

print "Main wait loop"
while True:
    try:
        time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        break

if scSensor:
    print "Closing speed sensor"
    scSensor.close()
    scSensor.unassign()
if powerMeter:
    print "Closing power meter"
    powerMeter.close()
    powerMeter.unassign()
print "Stopping ANT node"
antnode.stop()
