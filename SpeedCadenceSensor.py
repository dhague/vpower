from ant.core import event
from ant.core import message
from ant.core.constants import *

from config import SENSOR_TYPE, SENSOR_ID, LOG, DEBUG
from constants import SPEED_CADENCE_DEVICE_TYPE, SPEED_DEVICE_TYPE, CADENCE_DEVICE_TYPE


class SpeedCadenceSensor(event.EventCallback):
    def __init__(self, antnode):
        self.chanAssign = None
        self.currentData = None
        self.previousData = None
        self.deviceCfg = None
        self.revsPerSec = 0.0
        self.observer = None

        # Get the channel
        self.channel = antnode.getFreeChannel()
        self.channel.name = 'C:SPEED'
        self.channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
        self.channel.setID(SENSOR_TYPE, SENSOR_ID, 1)
        self.channel.setSearchTimeout(TIMEOUT_NEVER)
        if SENSOR_TYPE == SPEED_DEVICE_TYPE:
            period = 8118
        elif SENSOR_TYPE == CADENCE_DEVICE_TYPE:
            period = 8102
        elif SENSOR_TYPE == SPEED_CADENCE_DEVICE_TYPE:
            period = 8086
        self.channel.setPeriod(period)
        self.channel.setFrequency(57)

    def set_revs_per_sec(self, rps):
        self.revsPerSec = rps
        if self.observer:
            self.observer.update(self.revsPerSec)

    def notify_change(self, observer):
        self.observer = observer

    def open(self):
        # Open the channel
        self.channel.open()
        self.channel.registerCallback(self)  # -> will callback process() method below

    def close(self):
        self.channel.close()

    def unassign(self):
        self.channel.unassign()

    def stopped(self):
        # Question: how to detect if we are stopped?
        # Answer: heuristic - record timestamps of messages. If > 1 second between messages with
        # no change in speed data then we are stopped.
        # TODO
        return False

    def process(self, msg):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            dp = None
            # Get the datapage according to the configured device type
            if SENSOR_TYPE == SPEED_DEVICE_TYPE:
                dp = SpeedDataPage()
            elif SENSOR_TYPE == CADENCE_DEVICE_TYPE:
                dp = CadenceDataPage()
            elif SENSOR_TYPE == SPEED_CADENCE_DEVICE_TYPE:
                dp = SpeedCadenceDataPage()
            if dp is None:
                return

            message_data = SpeedCadenceData()
            dp.parse(msg.getPayload(), message_data)

            if DEBUG:
                message_data.print_speed()

            if self.currentData is None:
                self.previousData = self.currentData
                self.currentData = message_data
                return

            if not self.stopped() and message_data.speedEventTime != self.currentData.speedEventTime:
                # Calculate speed from previously-held data, if there is a change
                self.previousData = self.currentData
                self.currentData = message_data
                if self.previousData is not None:
                    current_event_time = self.currentData.speedEventTime
                    if current_event_time < self.previousData.speedEventTime:
                        current_event_time += 65536 / 1024.0
                    time_diff = current_event_time - self.previousData.speedEventTime
                    current_rev_count = self.currentData.speedRevCount
                    if current_rev_count < self.previousData.speedRevCount:
                        current_rev_count += 65536
                    revs_diff = current_rev_count - self.previousData.speedRevCount
                    self.set_revs_per_sec(revs_diff / time_diff)

        elif isinstance(msg, message.ChannelStatusMessage):
            if msg.getStatus() == EVENT_CHANNEL_CLOSED:
                # Channel closed, re-open
                open()


class SpeedCadenceData:
    def __init__(self):
        self.speedRevCount = None
        self.speedEventTime = None
        self.cadenceRevCount = None
        self.cadenceEventTime = None

    def print_speed(self):
        print 'speedRevCount: ', self.speedRevCount
        print 'speedEventTime: ', self.speedEventTime

    def print_cadence(self):
        print 'cadenceRevCount: ', self.cadenceRevCount
        print 'cadenceEventTime: ', self.cadenceEventTime


class DataPage(object):
    @staticmethod
    def parse_event_time(payload, offset):
        return (ord(payload[offset+1]) | (ord(payload[offset + 2]) << 8)) / 1024.0

    @staticmethod
    def parse_rev_count(payload, offset):
        return ord(payload[offset+1]) | (ord(payload[offset + 2]) << 8)


class SpeedDataPage(DataPage):
    def parse(self, payload, data):
        data.speedEventTime = self.parse_event_time(payload, 4)
        data.speedRevCount = self.parse_rev_count(payload, 6)


class CadenceDataPage(DataPage):
    def parse(self, payload, data):
        data.cadenceEventTime = self.parse_event_time(payload, 4)
        data.cadenceRevCount = self.parse_rev_count(payload, 6)


class SpeedCadenceDataPage(DataPage):
    def parse(self, payload, data):
        data.cadenceEventTime = self.parse_event_time(payload, 0)
        data.cadenceRevCount = self.parse_rev_count(payload, 2)
        data.speedEventTime = self.parse_event_time(payload, 4)
        data.speedRevCount = self.parse_rev_count(payload, 6)
