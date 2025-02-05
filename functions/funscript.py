import time
import numpy as np
import functions.serial as serialHelp


class Scripter():
    def __init__(self, baudRate, maxAnalog, sampleFrequency, maxPosition=100):

        self.maxAnalog = maxAnalog
        self.sampleFrequency = sampleFrequency
        self.maxPosition = maxPosition #"range" in the funscript metadata

        self.lastPosition = None
        self.startTime = None

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

        comPort = serialHelp.getComPort()

        time.sleep(0.1) #To ensure device is fully initiated

        self.serialReader = serialHelp.SerialReader(comPort, baudRate)

    def startRecording(self, length, lengthBuffer=3, print2terminal=False):
        '''
        length: Length of funscript in seconds (round up video length).
        lengthBuffer: Extra seconds incase the recording is not (perfectly) synced.
        '''
        length += lengthBuffer

        startTime = time.time()
        
        startPosition = self.getPosition()

        if startPosition is None:
            startPosition = self.lastPosition

        maximumPoints = length*self.sampleFrequency
        self.points = np.array(
            [np.zeros(maximumPoints, dtype=int), np.zeros(maximumPoints, dtype=int)])

        self.points[0][0] = 0
        self.points[1][0] = startPosition

        if print2terminal:
            print(f'[{self.points[0][0]}, {self.points[1][0]}]')

        i = 0
        currentTime = 0
        maxTime = length*1000

        while self.serialReader.isRunning():

            time.sleep(1/self.sampleFrequency)

            currentTime = round((time.time() - startTime)*1000)

            if currentTime > maxTime:
                break

            currentPosition = self.getPosition()

            if currentPosition is not None:

                i += 1

                if i > maximumPoints:
                    break

                self.points[0][i] = currentTime
                self.points[1][i] = currentPosition

                if print2terminal:
                    print(f'[{self.points[0][i]}, {self.points[1][i]}]')
        
        print(f'Logged {i+1} points!')

        trimmedTime = np.trim_zeros(self.points[0], 'b')
        trimmedPos = self.points[1][:len(trimmedTime)]

        self.points = np.array([trimmedTime, trimmedPos])

    def getPosition(self):
        '''
        Returns current funscript position if it has moved.
        '''
        
        currentPosition = round((self.serialReader.latestValue()/self.maxAnalog)*self.maxPosition)

        if currentPosition == self.lastPosition:
            return None
        
        self.lastPosition = currentPosition
        
        return currentPosition

