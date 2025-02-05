import functions.serial as serialHelp
import time
import signal
import rdppy

baudRate = 9600 #bits per second
resolution = 1024 #Android nano 10bits = 2^10
sampleFrequency = 100 #times per second

if __name__ == '__main__':

    comPort = serialHelp.getComPort()

    time.sleep(0.1) #To ensure device is fully initiated

    reader = serialHelp.serialReader(comPort, baudRate)

    def shutdown(signum, frame):
        reader.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    #Arduino int is 2 bytes
    updateFrequency = int(baudRate/(16))
    samplingRatio = updateFrequency/sampleFrequency

    print(
        f'Update frequency: {updateFrequency}\n'
        f'Sample frequency: {sampleFrequency}\n'
        f'Sampling ratio: {samplingRatio}')
    
    if samplingRatio < 2:
        raise RuntimeError(
            'Update frequency needs to be at least '
            'double the sample frequency to avoid sampling errors!')

    while reader.isRunning():
        print(reader.latestValue())

        time.sleep(1)

