import serial
import serial.tools.list_ports
import serial.serialutil
import threading
import time

class SerialReader:
    def __init__(self, comPort, baudrate):

        self.valueDict = [None, True]

        self.fetchThread = threading.Thread(
            target=lambda: serialReadLoop(self.valueDict, comPort, baudrate))
        
        self.fetchThread.start()

        while self.latestValue() is None:
            time.sleep(0.1)

        print(
            'Successfully connected to serial device '
            f'on comport "{comPort}"!')

    def latestValue(self):
        return self.valueDict[0]
    
    def isRunning(self):
        return self.valueDict[1]
    
    def stop(self):
        self.valueDict[1] = False

def serialReadLoop(returnList, comPort, baudrate):
    '''
    Reads serial value and converts to int 
    and adds it to index 0 of the given list.

    Index 1 of the list controls the while loop.
    '''

    ser = serial.Serial(comPort, baudrate)

    while returnList[1]:
        try:
            returnList[0] = int(ser.readline().decode().strip())

        except serial.serialutil.SerialException:
            print('Serial device disconnected!')
            returnList[1] = False

def getComPortList():
    '''
    Returns list with tuples (port, description)
    '''
    return [
        (str(port), desc.split(' ', 1)[0]) 
        for port, desc, _ in serial.tools.list_ports.comports()]

def getComPort(retryAttempts=100, retryWait=1):
    '''
    Returns serial com port.
    If there are more than one com port, ask user which one to use.

    retryAttempts: Times to retry search for a com port.
    retryWait: Time in seconds between retry attempts.
    '''
    portList = getComPortList()

    if len(portList) == 0:
        print(
            'No serial connection found.\n'
            'Please plug in serial device.')
        
        for i in range(retryAttempts + 1):
            time.sleep(retryWait)
            portList = getComPortList()

            if len(portList) != 0:
                break

            if i < retryAttempts:
                print(f'Retry attempt {i+1}/{retryAttempts}, retrying in {retryWait}s...')

        else:
            raise RuntimeError('Failed to determine serial device.')
    
    if len(portList) > 1:
        print(f'{len(portList)} serial devices found!')

        [print(f'{i}: {port} ({desc})') for i, (port, desc) in enumerate(portList, 1)]

        return portList[
            int(input('Please choose which serial device to use by inputting the corresponding number:\n').strip())][0]
    
    return portList[0][0]

def getExtremeValues(serialReader):
    '''
    Get minimum and maximum serial value from the device.

    Return min, max
    '''
    input('Set device to one min/max position then press enter.\n')

    value1 = serialReader.latestValue()

    input('Set device to one opposite min/max position then press enter.\n')

    value2 = serialReader.latestValue()

    if value1 > value2:
        return value2, value1
    
    return value1, value2

