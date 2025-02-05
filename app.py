import signal
import time
import functions.funscript as funscript


baudRate = 9600 #bits per second
maxAnalog = 1023 #Android nano 10bits > 2^10 = 1024 - 1 = 1023 (as signal starts at 0)
sampleFrequency = 100 #times per second


def countdown(seconds=3):
    input('Enter anything to start recording:\n')

    print('Starting in:')
    time.sleep(1)

    for i in range(seconds):
        print(f'{seconds - i}...')
        time.sleep(1)


if __name__ == '__main__':

    scripter = funscript.Scripter(baudRate, maxAnalog, sampleFrequency)

    def shutdown(signum, frame):
        scripter.serialReader.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    countdown()

    scripter.startRecording(length=5, print2terminal=True)

