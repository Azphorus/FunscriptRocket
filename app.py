import signal
import time
import functions.funscript as funscript


baudRate = 9600 #bits per second
sampleFrequency = 100 #times per second

#Video meta
title = 'testing'
creator = 'Anon'
length = 20 #seconds


def countdown(seconds=3):
    input('Press enter to start recording:\n')

    print('Starting in:')
    time.sleep(1)

    for i in range(seconds):
        print(f'{seconds - i}...')
        time.sleep(1)


if __name__ == '__main__':

    scripter = funscript.Scripter(baudRate, sampleFrequency, label=title)

    def shutdown(signum, frame):
        scripter.serialReader.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    countdown()

    points = scripter.startRecording(length=length, print2terminal=True)

    points = funscript.pointFilter(points)

    funscript.printFile(points, length, title=title, creator=creator)

