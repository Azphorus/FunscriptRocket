import functions
import time
import signal


baudRate = 9600


if __name__ == '__main__':

    reader = functions.serialReader(functions.getComPort(), baudRate)

    def shutdown(signum, frame):
        reader.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while reader.isRunning():
        print(reader.latestValue())
        time.sleep(1)

