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
    stuckCtr = 0
    failedCtr = 0
    iters = 0

    while (T > 0.1):
        nextState = generateNeighborState(curState, "SA")
        state_changed = False

        if nextState is curState:
            failedCtr += 1
        else:
            deltaE = calculateCost(nextState) - calculateCost(curState)

            if deltaE < 0:
                curState = nextState
                state_changed = True
            else:
                probability = math.exp(-deltaE / T)
                probabilityHistory.append((iters, probability))

                if probability > random.random():
                    curState = nextState
                    state_changed = True

        if not state_changed:
            stuckCtr += 1

        iters += 1
        costHistory.append(calculateCost(curState))
        T *= cooldownRate

    return curState, calculateCost(curState), costHistory, initState