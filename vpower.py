import time

# Initialize
from ant.core import driver
from ant.core import node

from BtAtsPowerCalculator import BtAtsPowerCalculator
from PowerMeterTx import PowerMeterTx
from SpeedCadenceSensorRx import SpeedCadenceSensorRx
from config import *

stick = driver.USB2Driver(None, log=LOG, debug=DEBUG)
antnode = node.Node(stick)
print "Starting ANT node"
antnode.start()
key = node.NetworkKey('N:ANT+', NETKEY)
antnode.setNetworkKey(0, key)

print "Starting speed sensor"
try:
    # Create the speed sensor object and open it
    speed_sensor = SpeedCadenceSensorRx(antnode)
    speed_sensor.open()
except Exception as e:
    print"speed_sensor  error: " + e.message
    speed_sensor = None

power_calculator = BtAtsPowerCalculator()

print "Check for temperature/pressure/humidity sensor"
try:
    import bme280

    temperature, pressure, humidity = bme280.readBME280All()
    print "Temp (C): " + repr(temperature)
    print "Pressure: " + repr(pressure)
    print "Humidity: " + repr(humidity)
    print "Air density: " + repr(power_calculator.calc_air_density(temperature, pressure, humidity))
    dynamic_air_density = True
except (ImportError, IOError) as e:
    dynamic_air_density = False
    print "Not found - assume air density of " + repr(AIR_DENSITY) + " kg/m3"
    power_calculator.air_density = AIR_DENSITY

# Notify the power calculator every time we get a speed event
speed_sensor.notify_change(power_calculator)

print "Starting power meter"
try:
    # Create the power meter object and open it
    power_meter = PowerMeterTx(antnode)
    power_meter.open()
except Exception as e:
    print "power_meter error: " + e.message
    power_meter = None

# Notify the power meter every time we get a calculated power value
power_calculator.notify_change(power_meter)

print "Main wait loop"
while True:
    try:
        if dynamic_air_density:
            temperature, pressure, humidity = bme280.readBME280All()
            if DEBUG:
                print "Temp (C): " + repr(temperature)
                print "Pressure: " + repr(pressure)
                print "Humidity: " + repr(humidity)
            power_calculator.update_air_density(temperature, pressure, humidity)
        time.sleep(AIR_DENSITY_UPDATE_SECS)
    except (KeyboardInterrupt, SystemExit):
        break

if speed_sensor:
    print "Closing speed sensor"
    speed_sensor.close()
    speed_sensor.unassign()
if power_meter:
    print "Closing power meter"
    power_meter.close()
    power_meter.unassign()
print "Stopping ANT node"
antnode.stop()
