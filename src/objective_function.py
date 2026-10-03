from read_write_file import *
from helper_function import *

def calculateTruckWeight(state, truck_index):
    total_weight = 0

    for state_package in state["in_trucks"][truck_index]["packages"]:
        package = getPackageById(state_package["id"])
        total_weight += package["weight"]

    return total_weight

def calculateTruckValue(state, truck_index):
    total_weight = 0

    for state_package in state["in_trucks"][truck_index]["packages"]:
        package = getPackageById(state_package["id"])
        total_weight += package["value"]

    return total_weight

def isPackageFlying(state, truck_index):
    truck_packages = state["in_trucks"][truck_index]["packages"]

    for state_package in truck_packages:
        package = getPackageById(state_package["id"])
        position = state_package["position"]
        dimension = getDimensionXYZ(package)

        if position["z"] == 0:
            continue

        is_supported = False

        for other_state_package in truck_packages:
            if other_state_package["id"] == state_package["id"]:
                continue

            other_package = getPackageById(other_state_package["id"])
            other_position = other_state_package["position"]
            other_dimension = getDimensionXYZ(other_package)

            other_top = other_position["z"] + other_dimension["z"]

            if other_top != position["z"]:
                continue

            x_overlap = (
                position["x"] < other_position["x"] + other_dimension["x"]
                and
                position["x"] + dimension["x"] > other_position["x"]                
            )

            y_overlap = (
                position["y"] < other_position["y"] + other_dimension["y"]
                and
                position["y"] + dimension["y"] > other_position["y"]                
            )

            if x_overlap and y_overlap:
                is_supported = True
                break

        if not is_supported:
            return True

    return False

def isPackageClipping(state, truck_index):
    truck_packages = state["in_trucks"][truck_index]["packages"]

    for i in range(len(truck_packages)):
        package1_state = truck_packages[i]
        package1 = getPackageById(package1_state["id"])
        pos1 = package1_state["position"]
        dim1 = getDimensionXYZ(package1)

        for j in range(i + 1, len(truck_packages)):
            package2_state = truck_packages[j]
            package2 = getPackageById(package2_state["id"])
            pos2 = package2_state["position"]
            dim2 = getDimensionXYZ(package2)

            x_overlap = (
                pos1["x"] < pos2["x"] + dim2["x"]
                and
                pos1["x"] + dim1["x"] > pos2["x"]                
            )

            y_overlap = (
                pos1["y"] < pos2["y"] + dim2["y"]
                and
                pos1["y"] + dim1["y"] > pos2["y"]                
            )

            z_overlap = (
                pos1["z"] < pos2["z"] + dim2["z"]
                and
                pos1["z"] + dim1["z"] > pos2["z"]                
            )

            if x_overlap and y_overlap and z_overlap:
                return True

    return False

def isFragileBelow(state, truck_index):
    truck_packages = state["in_trucks"][truck_index]["packages"]

    for state_package in truck_packages:
        package = getPackageById(state_package["id"])
        position = state_package["position"]
        dimension = getDimensionXYZ(package)

        for other_state_package in truck_packages:
            if other_state_package["id"] == state_package["id"]:
                continue

            other_package = getPackageById(other_state_package["id"])
            if not other_package["isFragile"]:
                continue

            other_position = other_state_package["position"]
            other_dimension = getDimensionXYZ(other_package)

            other_top = other_position["z"] + other_dimension["z"]

            current_bottom = position["z"]

            if other_top != current_bottom:
                continue

            x_overlap = (
                position["x"] < other_position["x"] + other_dimension["x"]
                and
                position["x"] + dimension["x"] > other_position["x"]                
            )

            y_overlap = (
                position["y"] < other_position["y"] + other_dimension["y"]
                and
                position["y"] + dimension["y"] > other_position["y"]                
            )

            if x_overlap and y_overlap:
                return True

    return False

def calculateCapacityPenalty(state):
    penalty = 0

    for truck in state["in_trucks"]["packages"]:
        weight = calculateTruckWeight(truck)

        current_id = truck["id"]

        if weight > trucks[current_id]["max_capacity"]:
            excess = max(0, weight - trucks[current_id]["max_capacity"])
            penalty += excess * 100

    return penalty

def calculateWarehousePenalty(state):
    weight = 0

    for warehouse in state["warehouse"]:
        weight += packages[warehouse]["weight"]

    return weight*20

def calculateCost(state): #nanti dituning ya gessss @fira @vari
    cost = 0
    
    cost += calculateCapacityPenalty(state)
    cost += calculateWarehousePenalty(state)

    if isFragileBelow(state):
        cost += 10000

    if isPackageClipping(state):
        cost += 10000

    if isPackageFlying(state):
        cost += 10000


