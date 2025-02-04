import serial
import serial.tools.list_ports
import time

def getComPortList():
    '''
    Returns list with tuples (port, description)
    '''
    return [
        (port, desc.split(' ', 1)[0]) 
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

        [print(f'{i}: {port} ({desc})') for i, (port, desc) in enumerate(getComPortList(), 1)]

        return portList[
            int(input('Please choose which serial device to use by inputting the corresponding number:').strip())]
    
    return portList[0]

