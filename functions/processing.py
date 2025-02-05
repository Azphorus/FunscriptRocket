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

    first = np.extract(dx[1:] * dx[:-1] < 0, npArray[0])
    second = np.extract(dx[1:] * dx[:-1] < 0, npArray[1])

    return np.array([first, second])

