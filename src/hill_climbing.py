from states import *
from objective_function import *


def hillClimbing():
    curState = generateRandomState()
    curCost = calculateCost(curState)
    costHistory = [curCost]

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
        else:
            break

    return curState, curCost, costHistory


def sideWaysHillClimbing():
    curState = generateRandomState()
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

    return curState, curCost, costHistory


def stochasticHillClimbing():
    curState = generateRandomState()
    curCost = calculateCost(curState)
    costHistory = [curCost]

    for i in range(100):
        neighbor = generateNeighborState(curState, "HC")
        if neighbor is curState:
            continue

        cost = calculateCost(neighbor)
        if cost < curCost:
            curState = neighbor
            curCost = cost

        costHistory.append(curCost)

    return curState, curCost, costHistory


def randomRestartHillClimbing():
    bestState = None
    bestCost = float('inf')
    allCostHistory = []

    for i in range(10):
        curState, curCost, costHistory = hillClimbing()
        allCostHistory.extend(costHistory)

        if curCost < bestCost:
            bestState = curState
            bestCost = curCost

    return bestState, bestCost, allCostHistory