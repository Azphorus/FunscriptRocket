import numpy as np
import scipy.ndimage
import rdppy

def removeOutliers(dataArray, range, index=1):
    '''
    Remove outliers in the specified index of the given 
    data array using a median filter.
    '''
    dataArray[index] = scipy.ndimage.median_filter(dataArray[index], size=range)

def rdpAlgorithm(dataArray, threshold=0.9):
    '''
    Vectorises the curve, removing points that follow straight lines 
    based on threshold value.

    returns processed array
    '''
    
    mask = rdppy.filter(dataArray.T, threshold)
    return np.array([np.array(dataArray[0])[mask], np.array(dataArray[1])[mask]])

