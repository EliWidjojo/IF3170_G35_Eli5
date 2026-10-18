from states import *
from objective_function import *


def hillClimbing():
    curState = generateRandomState()
    initState = deepCopyState(curState)
    curCost = calculateCost(curState)
    costHistory = [curCost]
    iters = 0

    for i in range(100):
        iters += 1
        bestNeighbor = None
        bestCost = float('inf')

        for j in range(50):
            neighbor = generateNeighborState(curState, "HC")
            if neighbor is curState:
                continue

            cost = calculateCost(neighbor)
            if cost < bestCost:
                bestNeighbor = neighbor
                bestCost = cost

        if bestNeighbor is None:
            break

        if bestCost < curCost:
            curState = bestNeighbor
            curCost = bestCost
        else:
            break

    return curState, curCost, costHistory, initState, iters


def sideWaysHillClimbing():
    curState = generateRandomState()
    initState = deepCopyState(curState)
    curCost = calculateCost(curState)
    costHistory = [curCost]
    sideWaysMoves = 0
    maxSideWaysMoves = 10

    for i in range(100):
        bestNeighbor = None
        bestCost = float('inf')

        for j in range(50):
            neighbor = generateNeighborState(curState, "HC")
            if neighbor is curState:
                continue

            cost = calculateCost(neighbor)
            if cost < bestCost:
                bestNeighbor = neighbor
                bestCost = cost

        if bestNeighbor is None:
            break

        if bestCost < curCost:
            curState = bestNeighbor
            curCost = bestCost
            costHistory.append(curCost)
            sideWaysMoves = 0

        elif bestCost == curCost and sideWaysMoves < maxSideWaysMoves:
            curState = bestNeighbor
            curCost = bestCost
            costHistory.append(curCost)
            sideWaysMoves += 1

        else:
            break

    return curState, curCost, costHistory, initState


def stochasticHillClimbing():
    curState = generateRandomState()
    initState = deepCopyState(curState)
    curCost = calculateCost(curState)
    costHistory = [curCost]

    for i in range(5000):
        neighbor = generateNeighborState(curState, "HC")
        if neighbor is curState:
            costHistory.append(curCost)
            continue

        cost = calculateCost(neighbor)
        if cost < curCost:
            curState = neighbor
            curCost = cost

        costHistory.append(curCost)

    return curState, curCost, costHistory, initState


def randomRestartHillClimbing():
    bestState = None
    bestCost = float('inf')
    allCostHistory = []
    itersPerRestart = []
    restarts = 0

    for i in range(10):
        restarts += 1
        curState, curCost, costHistory, initState, iters = hillClimbing()
        allCostHistory.extend(costHistory)
        itersPerRestart.append(iters)

        if curCost < bestCost:
            bestState = curState
            bestCost = curCost

    return bestState, bestCost, allCostHistory, initState, itersPerRestart, restarts