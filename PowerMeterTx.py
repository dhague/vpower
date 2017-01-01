from ant.core import message
from ant.core.constants import *

from constants import *
from config import POWER_SENSOR_ID, DEBUG

CHANNEL_PERIOD = 8182


# Transmitter for Bicycle Power ANT+ sensor
class PowerMeterTx(object):
    class PowerData:
        def __init__(self):
            self.eventCount = 0
            self.eventTime = 0
            self.cumulativePower = 0
            self.instantaneousPower = 0

    def __init__(self, antnode):
        self.antnode = antnode
        # Get the channel
        self.channel = antnode.getFreeChannel()
        self.channel.name = 'C:POWER'
        self.channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_TRANSMIT)
        self.channel.setID(POWER_DEVICE_TYPE, POWER_SENSOR_ID, 0)
        self.channel.setPeriod(8182)
        self.channel.setFrequency(57)
        self.powerData = PowerMeterTx.PowerData()

    def open(self):
        self.channel.open()

    def close(self):
        self.channel.close()

    def unassign(self):
        self.channel.unassign()

    # Power was updated, so send out an ANT+ message
    def update(self, power):
        if DEBUG: print 'PowerMeterTx: update called with power ', power
        self.powerData.eventCount = (self.powerData.eventCount + 1) & 0xff
        if DEBUG: print 'eventCount ', self.powerData.eventCount
        self.powerData.cumulativePower = (self.powerData.cumulativePower + int(power)) & 0xffff
        if DEBUG: print 'cumulativePower ', self.powerData.cumulativePower
        self.powerData.instantaneousPower = int(power)
        if DEBUG: print 'instantaneousPower ', self.powerData.instantaneousPower

        payload = chr(0x10)  # standard power-only message
        payload += chr(self.powerData.eventCount)
        payload += chr(0xFF)  # Pedal power not used
        payload += chr(0xFF)  # Cadence not used
        payload += chr(self.powerData.cumulativePower & 0xff)
        payload += chr(self.powerData.cumulativePower >> 8)
        payload += chr(self.powerData.instantaneousPower & 0xff)
        payload += chr(self.powerData.instantaneousPower >> 8)

        ant_msg = message.ChannelBroadcastDataMessage(self.channel.number, data=payload)
        if DEBUG: print 'Write message to ANT stick on channel ' + repr(self.channel.number)
        self.antnode.driver.write(ant_msg.encode())
