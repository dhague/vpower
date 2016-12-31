import time

# Initialize
from ant.core import driver
from ant.core import node

from BtAtsPowerCalculator import BtAtsPowerCalculator
from SpeedCadenceSensor import SpeedCadenceSensor
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
    scSensor = SpeedCadenceSensor(antnode)
    scSensor.open();
except Exception as e:
    print("scSensor: "+e.getMessage())
    scSensor = None

powerCalculator = BtAtsPowerCalculator()
scSensor.notify_change(powerCalculator)
powerBroadcaster = None
#powerCalculator.notifyChange(powerBroadcaster.powerChanged)

while True:
    try:
        time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        break;

if scSensor:
    print "Closing speed sensor"
    scSensor.close()
    scSensor.unassign()
if powerBroadcaster:
    powerBroadcaster.close()
    powerBroadcaster.unassign()
print "Stopping ANT node"
antnode.stop()
