import numpy as np
import scipy.ndimage
import rdppy

def removeOutliers(npArray, size=3, index=1):
    '''
    Remove outliers in the specified index of the given 
    data array using a median filter.
    '''
    npArray[index] = scipy.ndimage.median_filter(npArray[index], size=size)

def rdpAlgorithm(npArray, threshold=0.9):
    '''
    Vectorises the curve, removing points that follow straight lines 
    based on threshold value.

    returns processed array
    '''
    
    mask = rdppy.filter(npArray.T, threshold)
    return np.array([np.array(npArray[0])[mask], np.array(npArray[1])[mask]])

def turningPoints(npArray):
    '''
    Return an array only containing the turning points (where the derivative changes)
    '''

    dx = np.diff(npArray[1])

    mask = dx[1:] * dx[:-1] < 0

    first = np.array(npArray[0][1:-1])[mask]
    first = np.concatenate(([npArray[0][0]], first, [npArray[0][-1]]))

    second = np.array(npArray[1][1:-1])[mask]
    second = np.concatenate(([npArray[1][0]], second, [npArray[1][-1]]))

    return np.array([first, second])


def velocityFilter(npArray, threshold=0.1):
    '''
    Return an array only containing points where the derivative changes
    over the threshold value. Also includes any points returned by turningPoints.
    '''

    dx = np.diff(npArray[1])

    turningPoints = dx[1:] * dx[:-1] < 0
    velocity = abs(dx[1:] - dx[:-1]) > threshold
    mask = np.logical_or(turningPoints, velocity)

    first = np.array(npArray[0][1:-1])[mask]
    first = np.concatenate(([npArray[0][0]], first, [npArray[0][-1]]))

    second = np.array(npArray[1][1:-1])[mask]
    second = np.concatenate(([npArray[1][0]], second, [npArray[1][-1]]))

    return np.array([first, second])

def normalLength(line, point):
    '''
    Returns the distance from the point to the line.
    '''
    p1=np.array(line[0])
    p2=np.array(line[1])
    p3=np.array(point)

    return np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1)

def turningAndFurthest(npArray, threshold=1):
    '''
    First find turning points, then add the points between points of the
    turning point curve that is the further away than the threshold from the line created by 
    the turning point curve. Further add points if another point exceeds the threshold again.
    If points exceeding the threshold is less than the threshold from the previous point, 
    instead replace the previous point.
    '''
    returnList = [[], []]

    #Get turning mask and points
    dx = np.diff(npArray[1])

    mask = dx[1:] * dx[:-1] < 0
    mask = np.concatenate(([True], mask, [True])) #Add first and last points

    turningPoints = np.array([np.array(npArray[0])[mask], np.array(npArray[1])[mask]])

    j = 0
    for i, isTurning in enumerate(mask):

        if isTurning:
            if (j + 1) == len(turningPoints[0]):
                break

            line = [[turningPoints[0][j], turningPoints[1][j]], [turningPoints[0][j+1], turningPoints[1][j+1]]]

            j += 1

            extraPoints = []
            lastDistance = 0
            for k, point in enumerate(npArray[0][(i + 1):], 1):

                if mask[(i + k)] == True:
                    break

                middlePoint = [point, npArray[1][i + k]]

                distance = normalLength(line, middlePoint)

                if abs(distance - lastDistance) > threshold:
                    #Add point
                    extraPoints.append(middlePoint)
                    lastDistance = distance

                elif lastDistance != 0 and distance > lastDistance:
                    #Replace point
                    extraPoints[-1] = middlePoint

            returnList[0] += ([npArray[0][i]] + [p[0] for p in extraPoints])
            returnList[1] += ([npArray[1][i]] + [p[1] for p in extraPoints])

    return np.array(returnList, dtype=int)

