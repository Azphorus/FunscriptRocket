import time
import functions.serial as serialHelp


class Scripter():
    def __init__(self, baudRate, maxAnalog, maxPosition=100):

        self.maxAnalog = maxAnalog
        self.maxPosition = maxPosition #"range" in the funscript metadata

        comPort = serialHelp.getComPort()

        time.sleep(0.1) #To ensure device is fully initiated

        self.serialReader = serialHelp.SerialReader(comPort, baudRate)

        self.lastPosition = None

    def getPosition(self):
        '''
        Returns current funscript position if it has moved.
        '''
        
        currentPosition = round((self.serialReader.latestValue()/self.maxAnalog)*self.maxPosition)

        if currentPosition == self.lastPosition:
            return None
        
        self.lastPosition = currentPosition
        
        return currentPosition

