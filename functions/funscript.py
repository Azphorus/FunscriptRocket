import time
import numpy as np
import functions.serial as serialHelp
import functions.processing as processing


class Scripter():
    def __init__(self, baudRate, maxAnalog, sampleFrequency, label='unnamed', maxPosition=100):

        self.maxAnalog = maxAnalog
        self.sampleFrequency = sampleFrequency
        self.label = label
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

    def startRecording(self, length, lengthBuffer=3, print2terminal=False, appendTime=100):
        '''
        length: Length of funscript in seconds (round up video length).
        lengthBuffer: Extra seconds incase the recording is not (perfectly) synced.
        appendTime: Time in ms for when to append the last position a millisecond before current time.
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

        lastPosition = None
        lastTime = None

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

                if lastTime is not None:
                    if (currentTime - lastTime) > appendTime:
                        self.points[0][i] = currentTime - 1
                        self.points[1][i] = lastPosition
                        i += 1

                self.points[0][i] = currentTime
                self.points[1][i] = currentPosition

                lastTime = currentTime
                lastPosition = currentPosition

                if print2terminal:
                    print(f'[{self.points[0][i]}, {self.points[1][i]}]')
        
        print(f'Logged {i+1} points!')

        trimmedTime = np.trim_zeros(self.points[0], 'b')
        trimmedPos = self.points[1][:len(trimmedTime)]

        self.points = np.array([trimmedTime, trimmedPos])

        rawLabel = f'{self.label}_raw.txt'

        print(f'Saving raw output to file "{rawLabel}"...')
        np.savetxt(rawLabel, self.points, fmt='%d')
        
        print(f'Stopping serial reader...')
        self.serialReader.stop()

    def getPosition(self):
        '''
        Returns current funscript position if it has moved.
        '''
        
        currentPosition = round((self.serialReader.latestValue()/self.maxAnalog)*self.maxPosition)

        if currentPosition == self.lastPosition:
            return None
        
        self.lastPosition = currentPosition
        
        return currentPosition

def pointFilter(npArray, vectorThreshold=0.9, velocityThreshold=3, print2terminal=True):
    '''
    Vectorizes then 
    '''
    if print2terminal:
        print(f'Original length: {len(npArray[0])}')

    points = processing.rdpAlgorithm(points, threshold=vectorThreshold)

    if print2terminal:
        print(f'Vectorized: {len(points[0])}')

    points = processing.velocityFilter(points, threshold=velocityThreshold)

    if print2terminal:
        print(f'Velocity Filter: {len(points[0])}')

    return points

