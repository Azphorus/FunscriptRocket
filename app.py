import signal
import functions.funscript as funscript


baudRate = 9600 #bits per second
maxAnalog = 1023 #Android nano 10bits > 2^10 = 1024 - 1 = 1023 (as signal starts at 0)
sampleFrequency = 100 #times per second


if __name__ == '__main__':

    scripter = funscript.Scripter(baudRate, maxAnalog, sampleFrequency)

    def shutdown(signum, frame):
        scripter.serialReader.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    scripter.startRecording(length=10, print2terminal=True)

