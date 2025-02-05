import numpy as np
import random


def getSinWave(runtime=10, oscillation=1, sampleFrequency=100):
    '''
    Returns a 2D array with a timestamped sinwave.

    runtime: Time in seconds to run
    oscillation: Time in seconds for a full wave.
    sampleFrequency: Times per second to sample the sin wave.
    '''
    cycles = runtime/oscillation
    totalSamples = runtime*sampleFrequency
    runLength = np.pi * 2 * cycles

    return np.array([np.arange(0, runtime, 1/sampleFrequency), np.sin(np.arange(0, runLength, runLength / totalSamples))])

def addNoise(dataArray, noiseAxis=1, chance=0.3, maxSpike=1):
    '''
    chance: Chance of a spike to the signal (0 no spikes, 1 always spikes, 0.5 50% chance)
    '''
    for i, _ in enumerate(dataArray[noiseAxis]):
        if random.random() < chance:
            dataArray[noiseAxis][i] += maxSpike * random.random()

def createPseudoStroking(runtime=10, sampleFrequency=1000, range=100):
    '''
    Creates a pseudo stroking wave with noise.
    '''

    pseudoScript = getSinWave(runtime=runtime, sampleFrequency=sampleFrequency)

    pseudoScript[1] += 1
    pseudoScript[1] *= range/2

    addNoise(pseudoScript, chance=0.8, maxSpike=0.01) #general noise
    addNoise(pseudoScript, chance=0.01, maxSpike=10) #spikes

    return pseudoScript

