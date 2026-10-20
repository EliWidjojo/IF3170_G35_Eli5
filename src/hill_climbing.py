from states import *
from objective_function import *


def steepestAscentHillClimbing():
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
            costHistory.append(curCost)
        else:
            break

    return curState, curCost, costHistory, initState, iters


def sideWaysHillClimbing(maxSideWaysMoves=10):
    curState = generateRandomState()
    initState = deepCopyState(curState)
    curCost = calculateCost(curState)
    costHistory = [curCost]
    iters = 0
    sideWaysMoves = 0

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
            costHistory.append(curCost)
            sideWaysMoves = 0

        elif bestCost == curCost and sideWaysMoves < maxSideWaysMoves:
            curState = bestNeighbor
            curCost = bestCost
            costHistory.append(curCost)
            sideWaysMoves += 1

        else:
            break

    return curState, curCost, costHistory, initState, iters, sideWaysMoves


def stochasticHillClimbing():
    curState = generateRandomState()
    initState = deepCopyState(curState)
    curCost = calculateCost(curState)
    costHistory = [curCost]
    iters = 0

    for i in range(5000):
        iters += 1
        neighbor = generateNeighborState(curState, "HC")
        if neighbor is curState:
            costHistory.append(curCost)
            continue

        cost = calculateCost(neighbor)
        if cost < curCost:
            curState = neighbor
            curCost = cost

        costHistory.append(curCost)

    return curState, curCost, costHistory, initState, iters


def randomRestartHillClimbing(maxRestarts=10):
    bestState = None
    bestCost = float('inf')
    bestInitState = None
    allCostHistory = []
    itersPerRestart = []
    restarts = 0
    totalIters = 0

    for i in range(maxRestarts):
        restarts += 1
        curState, curCost, costHistory, initState, iters = steepestAscentHillClimbing()
        allCostHistory.extend(costHistory)
        itersPerRestart.append(iters)

        if curCost < bestCost:
            bestState = curState
            bestCost = curCost
            bestInitState = initState

    totalIters = sum(itersPerRestart)

    return bestState, bestCost, allCostHistory, bestInitState, itersPerRestart, restarts, totalIters