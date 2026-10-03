from read_write_file import *
from objective_function import *
import random

# bentuk state:
# state = {
#   "in_warehouse": [packages]
#   "in_trucks": [
#       "truck": id_truck
#       "packages": [
#           "id": id_package
#           "position": {x: ..., y: ..., z: ...}
#        ]
#    ]
#}


def generateRandomState():
    state = {
        "in_warehouse" : [],
        "in_trucks" : []
    }

    in_trucks = []

    # create empty trucks
    for truck in trucks:
        in_trucks.append({
            "truck": truck["id"],
            "packages" : []
        })

    # load packages to truck
    shuffled_packages = packages.copy()
    random.shuffle(shuffled_packages)

    for package in packages:
        possible_trucks = []

        for truck_index, truck in enumerate(trucks):
            weight = calculateTruckWeight(state, truck_index)

            if weight + package["weight"] <= truck["max_capacity"]:
                possible_trucks.append(truck_index)

        if possible_trucks:
            truck_index = random.choice(possible_trucks)
            state["in_trucks"][truck_index]["packages"].append({
                "id": package["id"],
                "position": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                }
            })
        else:
            state["in_warehouse"].append(package["id"])

    return state


