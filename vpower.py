#!/usr/bin/env python3
import time
import platform

from ant.core import driver
from ant.core import node

from usb.core import find

from PowerMeterTx import PowerMeterTx
from SpeedCadenceSensorRx import SpeedCadenceSensorRx
from config import DEBUG, LOG, NETKEY, POWER_CALCULATOR, POWER_SENSOR_ID, SENSOR_TYPE, SPEED_SENSOR_ID

antnode = None
speed_sensor = None
power_meter = None

def stop_ant():
    if speed_sensor:
        print("Closing speed sensor")
        speed_sensor.close()
        speed_sensor.unassign()
    if power_meter:
        print("Closing power meter")
        power_meter.close()
        power_meter.unassign()
    if antnode:
        print("Stopping ANT node")
        antnode.stop()

pywin32 = False
if platform.system() == 'Windows':
    def on_exit(sig, func=None):
        stop_ant()
    try:
        import win32api
        win32api.SetConsoleCtrlHandler(on_exit, True)
        pywin32 = True
    except ImportError:
        print("Warning: pywin32 is not installed, use Ctrl+C to stop")

try:
    print("Using " + POWER_CALCULATOR.__class__.__name__)

    devs = find(find_all=True, idVendor=0x0fcf)
    for dev in devs:
        if dev.idProduct in [0x1008, 0x1009]:
            # If running on the same PC as the receiver app (with two identical sticks)
            # the first stick may be already claimed, so continue trying
            stick = driver.USB2Driver(log=LOG, debug=DEBUG, idProduct=dev.idProduct, bus=dev.bus, address=dev.address)
            try:
                stick.open()
            except:
                continue
            stick.close()
            break
    else:
        print("No ANT devices available")
        exit()

    antnode = node.Node(stick)
    print("Starting ANT node")
    antnode.start()
    key = node.Network(NETKEY, 'N:ANT+')
    antnode.setNetworkKey(0, key)

    print("Starting speed sensor")
    try:
        # Create the speed sensor object and open it
        speed_sensor = SpeedCadenceSensorRx(antnode, SENSOR_TYPE, SPEED_SENSOR_ID & 0xffff)
        speed_sensor.open()
        # Notify the power calculator every time we get a speed event
        speed_sensor.notify_change(POWER_CALCULATOR)
    except Exception as e:
        print("speed_sensor error: " + repr(e))
        speed_sensor = None

    print("Starting power meter with ANT+ ID " + repr(POWER_SENSOR_ID))
    try:
        # Create the power meter object and open it
        power_meter = PowerMeterTx(antnode, POWER_SENSOR_ID)
        power_meter.open()
    except Exception as e:
        print("power_meter error: " + repr(e))
        power_meter = None

    # Notify the power meter every time we get a calculated power value
    POWER_CALCULATOR.notify_change(power_meter)

    stopped = True
    last_time = 0
    last_update = 0
    print("Main wait loop")
    while True:
        try:
            # Some apps keep the last received power value if the sensor stops broadcasting
            # and some drop the power to zero if the interval between updates is > 1 second
            if not stopped:
                t = int(time.time())
                if t >= last_update + 3:
                    if speed_sensor.currentData.speedEventTime == last_time:
                        # Set power to zero if speed sensor doesn't update for 3 seconds
                        power_meter.powerData.instantaneousPower = 0
                        stopped = True
                    last_time = speed_sensor.currentData.speedEventTime
                    last_update = t
                # Force an update every second to avoid power drops
                power_meter.update(power_meter.powerData.instantaneousPower)
            elif power_meter.powerData.instantaneousPower:
                stopped = False
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            break

except Exception as e:
    print("Exception: " + repr(e))
finally:
    if not pywin32:
        stop_ant()
