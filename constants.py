SPEED_DEVICE_TYPE = 0x7B
CADENCE_DEVICE_TYPE = 0x7A
SPEED_CADENCE_DEVICE_TYPE = 0x79
POWER_DEVICE_TYPE = 0x0B


# Get the serial number of Raspberry Pi
def getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"

    return cpuserial
