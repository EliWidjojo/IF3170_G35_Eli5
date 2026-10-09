from states import *
from objective_function import *
import random
import json

def tournamentSelection(population):
    candidates = random.sample(population, 5)
    return min(candidates, key=calculateCost)

def crossover(parent1, parent2):
    # bikin truck anak
    child = {
        "in_warehouse": [],
        "in_trucks": []
    }

    for truck in parent1["in_trucks"]:
        child["in_trucks"].append({
            "truck": truck["truck"],
            "packages": []
        })

    package_ids = []

    for package_id in parent1["in_warehouse"]:
        package_ids.append(package_id)

    for truck in parent1["in_trucks"]:
        for package in truck["packages"]:
            package_ids.append(package["id"])

    # Crossover per package
    for package_id in package_ids:

        if random.random() < 0.5:
            source = parent1
        else:
            source = parent2

        placement = getPackagePlacement(source, package_id)

        if placement["location"] == "warehouse":
            child["in_warehouse"].append(placement["package"])

        else:
            for truck in child["in_trucks"]:
                if truck["truck"] == placement["truck"]:
                    truck["packages"].append(placement["package"])
                    break

    return child

def calculateDiversity(population):
    uniqueStates = {
        json.dumps(state, sort_keys=True)
        for state in population
    }

    return len(uniqueStates)

def geneticAlgorithm(populationSize = 100, generations= 100):
    population = []
    costHistory = []

    for i in range(populationSize):
        population.append(generateRandomState())

    best = min(population, key=lambda x: calculateCost(x))
    bestCost = calculateCost(best)
    initState = deepCopyState(best)
    costHistory = [calculateCost(best)]
    avgCostHistory = [
        sum(calculateCost(x) for x in population) / len(population)
    ]

    for generation in range(generations):
        newPopulation = []

        while len(newPopulation) < len(population):
            parent1 = tournamentSelection(population)
            parent2 = tournamentSelection(population)

            child = crossover(parent1, parent2)
            if random.random() < 0.25:
                child = generateNeighborState(child, "GA")

            newPopulation.append(child)

        population = newPopulation
        best = min(population, key=lambda x: calculateCost(x))
        bestCost = calculateCost(best)

        costHistory.append(bestCost)
        avgCostHistory.append(
            sum(calculateCost(x) for x in population) / len(population)
        )

    best = min(population, key = lambda x : calculateCost(x))
    bestCost = calculateCost(best)

    return best, bestCost, costHistory, initState, avgCostHistory, generations