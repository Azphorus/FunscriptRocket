import time
import json
import numpy as np
import functions.serial as serialHelp
import functions.processing as processing


class Scripter():
    def __init__(self, baudRate, sampleFrequency, label='unnamed', maxPosition=100):

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

        self.minAnalog, self.maxAnalog = serialHelp.getExtremeValues(self.serialReader)

        print(f'Min signal: {self.minAnalog}\nMax signal: {self.maxAnalog}')

        self.analogRange = self.maxAnalog - self.minAnalog

    def startRecording(self, length, print2terminal=False, appendTime=100):
        '''
        length: Length of funscript in seconds (round up video length).
        appendTime: Time in ms for when to append the last position a millisecond before current time.
        '''

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

        return self.points
    
    def filterAnalog(self):
        '''
        Return filtered serial value.
        '''
        analogValue = self.serialReader.latestValue()

        if analogValue > self.maxAnalog:
            return self.analogRange
        
        elif analogValue < self.minAnalog:
            return 0
        
        return analogValue - self.minAnalog

    def getPosition(self):
        '''
        Returns current funscript position if it has moved.
        '''
        
        currentPosition = round((self.filterAnalog()/self.analogRange)*self.maxPosition)

        if currentPosition == self.lastPosition:
            return None
        
        self.lastPosition = currentPosition
        
        return currentPosition

def pointFilter(npArray, rdp1=0.9, minStep=3, rdp2=4, print2terminal=True):
    '''
    Vectorizes then 
    '''
    if print2terminal:
        print(
            f'Original length: {len(npArray[0])}\n'
            f'Applying RDP filter with threshold {rdp1}...')

    points = processing.rdpAlgorithm(npArray, threshold=rdp1)

    if print2terminal:
        print(
            f'RDP Filter pass one: {len(points[0])}\n'
            f'Applying min filter with step {minStep}...')
    
    processing.minimumStep(points, minStep=minStep)

    if print2terminal:
        print('Applying turning filter...')
    
    points = processing.turningPoints(points)

    if print2terminal:
        print(
            f'Turning filter: {len(points[0])}\n'
            f'Applying RDP filter with threshold {rdp2}...')

    points = processing.rdpAlgorithm(points, threshold=rdp2)

    if print2terminal:
        print(f'RDP Filter pass two: {len(points[0])}')

    return points

def printFile(npArray, duration, range=100, title='unnamed', version=1.0, inverted=False, creator='', description='', license='', performerList=[], script_url='', tagList=[], video_url='', type=''):
    '''
    Print funscript file.
    '''

    funDict = {}

    funDict['version'] = version
    funDict['inverted'] = inverted
    funDict['range'] = range

    actionList = []
    metaDict = {}

    funDict['actions'] = actionList
    funDict['metadata'] = metaDict

    metaDict['title'] = title
    metaDict['duration'] = duration

    for stringInput in [creator, description, license, script_url, video_url, type]:
        metaDict[stringInput] = stringInput

    if len(performerList) != 0:
        metaDict['performers'] = performerList
    
    if len(tagList) != 0:
        metaDict['tags'] = tagList

    for i, position in enumerate(npArray[1]):
        actionList.append({
            'pos': int(position),
            'at': int(npArray[0][i])})
    
    filename = f'{title}.funscript'
    print(f'Writing "{filename}"...')

    with open(filename, 'w') as funFile:
        funFile.write(json.dumps(funDict))

