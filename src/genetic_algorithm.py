from states import *
from objective_function import *
import random

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

def mutate(state):
    if random.random() < 0.1:
        state = generateNeighborState(state, "GA")
    return state

def geneticAlgorithm():
    population = []
    costHistory = []

    for i in range(100):
        population.append(generateRandomState())

    best = min(population, key=lambda x: calculateCost(x))
    bestCost = calculateCost(best)
    initState = deepCopyState(best)

    for generation in range(100):
        newPopulation = []

        while len(newPopulation) < len(population):
            parent1 = tournamentSelection(population)
            parent2 = tournamentSelection(population)

            child = crossover(parent1, parent2)
            child = mutate(child)

            newPopulation.append(child)

        population = newPopulation
        best = min(population, key=lambda x: calculateCost(x))
        bestCost = calculateCost(best)

        costHistory.append(bestCost)

    best = min(population, key = lambda x : calculateCost(x))
    bestCost = calculateCost(best)

    return best, bestCost, costHistory, initState