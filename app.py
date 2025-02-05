import time
import signal
import functions.funscript as funscript


baudRate = 9600 #bits per second
maxAnalog = 1023 #Android nano 10bits > 2^10 = 1024 - 1 = 1023 (as signal starts at 0)
sampleFrequency = 100 #times per second

if __name__ == '__main__':

    scripter = funscript.Scripter(baudRate, maxAnalog)

    def shutdown(signum, frame):
        scripter.serialReader.stop()

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

    while scripter.serialReader.isRunning():

        position = scripter.getPosition()

        if position is not None:
            print(position)

        time.sleep(1/sampleFrequency)

