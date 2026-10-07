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

def getFlyingPackages(state, truck_index):
    truck_packages = state["in_trucks"][truck_index]["packages"]
    flying = []

    for sp in truck_packages:
        pkg = getPackageById(sp["id"])
        pos = sp["position"]
        dim = getDimensionXYZ({
            "dimension": pkg["dimension"],
            "orientation": sp["orientation"]
        })

        if pos["z"] == 0:
            continue

        is_supported = False

        for osp in truck_packages:
            if osp["id"] == sp["id"]:
                continue

            opkg = getPackageById(osp["id"])
            opos = osp["position"]
            odim = getDimensionXYZ({
                "dimension": opkg["dimension"],
                "orientation": osp["orientation"]
            })

            other_top = opos["z"] + odim["z"]
            if other_top != pos["z"]:
                continue

            x_overlap = (pos["x"] < opos["x"] + odim["x"] and pos["x"] + dim["x"] > opos["x"])
            y_overlap = (pos["y"] < opos["y"] + odim["y"] and pos["y"] + dim["y"] > opos["y"])

            if x_overlap and y_overlap:
                is_supported = True
                break

        if not is_supported:
            flying.append(sp["id"])

    return flying

def isPackageFlying(state, truck_index):
    return len(getFlyingPackages(state, truck_index)) > 0
      
def getClippingPairs(state, truck_index):
    truck_packages = state["in_trucks"][truck_index]["packages"]
    pairs = []

    for i in range(len(truck_packages)):
        p1s = truck_packages[i]
        p1 = getPackageById(p1s["id"])
        pos1 = p1s["position"]
        dim1 = getDimensionXYZ({
            "dimension": p1["dimension"],
            "orientation": p1s["orientation"]
        })

        for j in range(i + 1, len(truck_packages)):
            p2s = truck_packages[j]
            p2 = getPackageById(p2s["id"])
            pos2 = p2s["position"]
            dim2 = getDimensionXYZ({
                "dimension": p2["dimension"],
                "orientation": p2s["orientation"]
            })

            x_overlap = (pos1["x"] < pos2["x"] + dim2["x"] and pos1["x"] + dim1["x"] > pos2["x"])
            y_overlap = (pos1["y"] < pos2["y"] + dim2["y"] and pos1["y"] + dim1["y"] > pos2["y"])
            z_overlap = (pos1["z"] < pos2["z"] + dim2["z"] and pos1["z"] + dim1["z"] > pos2["z"])

            if x_overlap and y_overlap and z_overlap:
                pairs.append((p1s["id"], p2s["id"]))

    return pairs

def isPackageClipping(state, truck_index):
    return len(getClippingPairs(state, truck_index)) > 0

def getFragileViolations(state, truck_index):
    truck_packages = state["in_trucks"][truck_index]["packages"]
    violations = []

    for sp in truck_packages:
        pkg = getPackageById(sp["id"])
        pos = sp["position"]
        dim = getDimensionXYZ({
            "dimension": pkg["dimension"],
            "orientation": sp["orientation"]
        })

        for osp in truck_packages:
            if osp["id"] == sp["id"]:
                continue

            opkg = getPackageById(osp["id"])
            if not opkg["isFragile"]:
                continue

            opos = osp["position"]
            odim = getDimensionXYZ({
                "dimension": opkg["dimension"],
                "orientation": osp["orientation"]
            })

            other_top = opos["z"] + odim["z"]
            if other_top != pos["z"]:
                continue

            x_overlap = (pos["x"] < opos["x"] + odim["x"] and pos["x"] + dim["x"] > opos["x"])
            y_overlap = (pos["y"] < opos["y"] + odim["y"] and pos["y"] + dim["y"] > opos["y"])

            if x_overlap and y_overlap:
                violations.append((sp["id"], osp["id"]))

    return violations

def isFragileBelow(state, truck_index):
    return len(getFragileViolations(state, truck_index)) > 0

def getOutOfBoundsPackages(state, truck_index):
    truck_data = trucks[truck_index]
    truck_packages = state["in_trucks"][truck_index]["packages"]
    out = []

    for sp in truck_packages:
        pkg = getPackageById(sp["id"])
        dim = getDimensionXYZ({
            "dimension": pkg["dimension"],
            "orientation": sp["orientation"]
        })
        pos = sp["position"]

        if (pos["x"] < 0 or pos["y"] < 0 or pos["z"] < 0 or
            pos["x"] + dim["x"] > truck_data["dimension"]["w"] or
            pos["y"] + dim["y"] > truck_data["dimension"]["l"] or
            pos["z"] + dim["z"] > truck_data["dimension"]["h"]):
            out.append(sp["id"])

    return out

def isPackageOutOfBounds(state, truck_index):
    return len(getOutOfBoundsPackages(state, truck_index)) > 0

def calculateCapacityPenalty(state):
    penalty = 0

    for truck_index, truck in enumerate(state["in_trucks"]):
        truck_id = truck["truck"]

        weight = calculateTruckWeight(state, truck_index)

        truck_data = next(
            t for t in trucks
            if t["id"] == truck_id
        )

        if weight > truck_data["max_capacity"]:
            excess = weight - truck_data["max_capacity"]
            penalty += excess * 100

    return penalty

def calculateWarehousePenalty(state):
    weight = 0

    for package_id in state["in_warehouse"]:
        package = next(
            p for p in packages
            if p["id"] == package_id
        )

        weight += package["weight"]

    return weight * 20

def calculateTotVal(state):
    total_value = 0

    for truck_index in range(len(state["in_trucks"])):
        total_value += calculateTruckValue(state, truck_index)

    return total_value

def calculateCost(state):
    cost = 0

    cost -= calculateTotVal(state)
    cost += calculateCapacityPenalty(state)
    cost += calculateWarehousePenalty(state)

    for truck_index in range(len(state["in_trucks"])):
        cost += ((len(getClippingPairs(state, truck_index)) + len(getFlyingPackages(state, truck_index)) + 
                 len(getFragileViolations(state, truck_index)) + len(getOutOfBoundsPackages(state, truck_index))) 
                 * 10000)

    return cost