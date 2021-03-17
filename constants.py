import platform

SPEED_DEVICE_TYPE = 0x7B
CADENCE_DEVICE_TYPE = 0x7A
SPEED_CADENCE_DEVICE_TYPE = 0x79
POWER_DEVICE_TYPE = 0x0B


# Get the serial number of Raspberry Pi or PC CPU (Windows)
def getserial():
    cpuserial = "0000000000000000"
    try:
        if platform.system() == 'Windows':
            # Extract serial from wmic command
            from subprocess import check_output
            cpuserial = check_output('wmic cpu get ProcessorId').decode().split('\n')[1].strip()
        else:
            # Extract serial from cpuinfo file
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
            f.close()
    except:
        cpuserial = "ERROR000000000"

    return cpuserial
