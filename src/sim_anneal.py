from states import *
from objective_function import *
import math
import random
import time

def simulatedAnnealing():
    T = 300
    cooldownRate = 0.999
    curState = generateRandomState()
    initState = deepCopyState(curState)
    costHistory = [calculateCost(curState)]
    probabilityHistory = []
    rejectedWorseMoves = 0
    iters = 0

    while (T > 0.1):
        nextState = generateNeighborState(curState, "SA")
        deltaE = calculateCost(nextState) - calculateCost(curState)

        if deltaE <= 0:
            curState = nextState
        else:
            probability = math.exp(-deltaE / T)
            probabilityHistory.append((iters, probability))

            if probability > random.random():
                curState = nextState
            else: 
                rejectedWorseMoves += 1 

        iters += 1
        costHistory.append(calculateCost(curState))
        T *= cooldownRate

    return curState, calculateCost(curState), costHistory, initState, probabilityHistory, rejectedWorseMoves, iters