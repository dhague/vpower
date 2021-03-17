from ant.core import event, message, node
from ant.core.constants import *

from constants import *
from config import NETKEY, VPOWER_DEBUG


# Receiver for Speed and/or Cadence ANT+ sensor
class SpeedCadenceSensorRx(event.EventCallback):
    def __init__(self, antnode, sensor_type, sensor_id):
        self.sensor_type = sensor_type
        self.sensor_id = sensor_id
        self.currentData = None
        self.previousData = None
        self.revsPerSec = 0.0
        self.observer = None

        # Get the channel
        self.channel = antnode.getFreeChannel()
        self.channel.name = 'C:SPEED'
        network = node.Network(NETKEY, 'N:ANT+')
        self.channel.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
        self.channel.setID(sensor_type, sensor_id, 0)
        self.channel.searchTimeout = TIMEOUT_NEVER
        if sensor_type == SPEED_DEVICE_TYPE:
            period = 8118
        elif sensor_type == CADENCE_DEVICE_TYPE:
            period = 8102
        elif sensor_type == SPEED_CADENCE_DEVICE_TYPE:
            period = 8086
        self.channel.period = period
        self.channel.frequency = 57

    def set_revs_per_sec(self, rps):
        self.revsPerSec = rps
        if self.observer:
            self.observer.update(self.revsPerSec)

    def notify_change(self, observer):
        self.observer = observer

    def open(self):
        self.channel.open()
        self.channel.registerCallback(self)  # -> will callback process(msg) method below

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

    def process(self, msg, channel):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            dp = None
            # Get the datapage according to the configured device type
            if self.sensor_type == SPEED_DEVICE_TYPE:
                dp = SpeedDataPage()
            elif self.sensor_type == CADENCE_DEVICE_TYPE:
                dp = CadenceDataPage()
            elif self.sensor_type == SPEED_CADENCE_DEVICE_TYPE:
                dp = SpeedCadenceDataPage()
            if dp is None:
                return

            # Parse the incoming message into a SpeedCadenceData object
            message_data = SpeedCadenceData()
            dp.parse(msg.data, message_data)

            if VPOWER_DEBUG: message_data.print_speed()

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
            if msg.status == EVENT_CHANNEL_CLOSED:
                # Channel closed, re-open
                open()


class SpeedCadenceData:
    def __init__(self):
        self.speedRevCount = None
        self.speedEventTime = None
        self.cadenceRevCount = None
        self.cadenceEventTime = None

    def print_speed(self):
        print('speedRevCount: ', self.speedRevCount)
        print('speedEventTime: ', self.speedEventTime)

    def print_cadence(self):
        print('cadenceRevCount: ', self.cadenceRevCount)
        print('cadenceEventTime: ', self.cadenceEventTime)


class DataPage(object):
    @staticmethod
    def parse_event_time(payload, offset):
        return (payload[offset] | (payload[offset + 1] << 8)) / 1024.0

    @staticmethod
    def parse_rev_count(payload, offset):
        return payload[offset] | (payload[offset + 1] << 8)


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
