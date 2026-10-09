from read_write_file import *
from objective_function import *
import random
from itertools import permutations

# bentuk state:
# state = {
#   "in_warehouse": [packages]
#   "in_trucks": [
#       "truck": id_truck
#       "packages": [
#           "id": id_package
#           "position": {x: ..., y: ..., z: ...}
#           "orientation": {w: ..., l: ..., h: ...}
#        ]
#    ]
#}

# generate random state
def generateRandomState():
    state = {
        "in_warehouse" : [],
        "in_trucks" : []
    }

    # create empty trucks
    for truck in trucks:
        state["in_trucks"].append({
            "truck" : truck["id"],
            "packages" : []
        })

    # load packages to truck
    shuffled_packages = packages.copy()
    random.shuffle(shuffled_packages)

    for package in shuffled_packages:
        possible_trucks = getTrucksWithCapacity(state, package)

        random.shuffle(possible_trucks)
        placed = False

        for truck_index in possible_trucks:
            placed = tryPlacePackage(state, truck_index, package)
            if placed:
                break

        if not placed:
            state["in_warehouse"].append(package["id"])

    return state

def deepCopyState(state):
    new_trucks = []

    for truck in state["in_trucks"]:
        new_packages = []

        for package in truck["packages"]:
            new_packages.append({
                "id": package["id"],
                "position": dict(package["position"]),
                "orientation": dict(package["orientation"])
            })

        new_trucks.append({
            "truck": truck["truck"],
            "packages": new_packages
        })

    return {
        "in_warehouse": state["in_warehouse"].copy(),
        "in_trucks": new_trucks
    }

# coba taruh 1 paket ke 1 truk tertentu
def tryPlacePackage(state, truck_index, package):
    truck_data = trucks[truck_index]
    for _ in range(50):
        # random orientasi
        w, l, h = random.sample(["x", "y", "z"], 3)
        orientation = {"w": w, "l": l, "h": h}
    
        orientation_package = {
            "id": package["id"],
            "dimension": package["dimension"],
            "orientation": orientation
        }
    
        dim = getDimensionXYZ(orientation_package)

        # skip kalo dimensi paket lbh dr truk
        if (dim["x"] > truck_data["dimension"]["w"] or dim["y"] > truck_data["dimension"]["l"] or dim["z"] > truck_data["dimension"]["h"]):
            continue
        else: 
            # random posisi di dlm truk
            pos_x = random.randint(0, truck_data["dimension"]["w"] - dim["x"])
            pos_y = random.randint(0, truck_data["dimension"]["l"] - dim["y"])
            pos_z = random.randint(0, truck_data["dimension"]["h"] - dim["z"])
    
            state["in_trucks"][truck_index]["packages"].append({
                "id": package["id"],
                "position": {"x": pos_x, "y": pos_y, "z": pos_z},
                "orientation": orientation
            })
        
            return True
                
    return False

# remove paket dari truk
def removePackageFromTruck(state, truck_index, package_id):
    truck = state["in_trucks"][truck_index]
    
    for i, package in enumerate(truck["packages"]):
        if package["id"] == package_id:
            del truck["packages"][i]
            return True
        
    return False

# milih truk random yang masih ada isinya
def chooseRandomSourceTruck(state):
    truck_candidates = []
    for i, truck in enumerate(state["in_trucks"]):
        if len(truck["packages"]) > 0: # cari truk yg ada isinya
            truck_candidates.append(i)

    if not truck_candidates:
        return None

    return random.choice(truck_candidates)

# nyari truk yang masih muat utk paket tertentu
def getTrucksWithCapacity(state, package, exclude_index=None):
    possible_trucks = []
    
    for i, truck in enumerate(state["in_trucks"]):
        if i == exclude_index:
            continue
        
        if calculateTruckWeight(state, i) + package["weight"] <= trucks[i]["max_capacity"]:
            possible_trucks.append(i)
    
    return possible_trucks

# pilih 1 paket dr truk a trs pindahin ke truk b
def movePackageBetweenTrucks(state):
    truck_a = chooseRandomSourceTruck(state)
    if truck_a is None:
        return False

    package = random.choice(state["in_trucks"][truck_a]["packages"])

    truck_b_candidates = getTrucksWithCapacity(state, getPackageById(package["id"]), exclude_index=truck_a)
    if not truck_b_candidates:
        return False

    truck_b = random.choice(truck_b_candidates)

    # pindah paket kalo bisa
    removePackageFromTruck(state, truck_a, package["id"])

    if tryPlacePackage(state, truck_b, getPackageById(package["id"])):
        return True
    
    else: # rollback kalo gagal pindah
        state["in_trucks"][truck_a]["packages"].append(package)
        return False

# tukar masing" 1 paket dr truk a dan truk b
def swapPackageBetweenTrucks(state):
    truck_a = chooseRandomSourceTruck(state)
    if truck_a is None:
        return False

    package_a = random.choice(state["in_trucks"][truck_a]["packages"])
    w_a = calculateTruckWeight(state, truck_a)
    w_pkg_a = getPackageById(package_a["id"])["weight"]

    pkg_b_candidates = []

    for truck_b_index, truck_b in enumerate(state["in_trucks"]):
        if truck_b_index == truck_a or len(truck_b["packages"]) == 0:
            continue

        w_b = calculateTruckWeight(state, truck_b_index)
        valid_pkg_b = []

        for package_b in truck_b["packages"]:
            w_pkg_b = getPackageById(package_b["id"])["weight"]
            w_a_new = w_a - w_pkg_a + w_pkg_b
            w_b_new = w_b - w_pkg_b + w_pkg_a

            # cek apakah masih muat
            if (w_a_new <= trucks[truck_a]["max_capacity"] and w_b_new <= trucks[truck_b_index]["max_capacity"]):
                valid_pkg_b.append(package_b)

        if valid_pkg_b:
            package_b = random.choice(valid_pkg_b)
            pkg_b_candidates.append((truck_b_index, package_b))

    if not pkg_b_candidates:
        return False

    truck_b_index, package_b = random.choice(pkg_b_candidates)

    # coba swap paket
    removePackageFromTruck(state, truck_a, package_a["id"])
    removePackageFromTruck(state, truck_b_index, package_b["id"])
    placed_b_in_a = tryPlacePackage(state, truck_a, getPackageById(package_b["id"]))
    placed_a_in_b = tryPlacePackage(state, truck_b_index, getPackageById(package_a["id"]))

    if placed_b_in_a and placed_a_in_b:
        return True

    # rollback kalo gagal swap
    if placed_b_in_a:
        removePackageFromTruck(state, truck_a, package_b["id"])
    if placed_a_in_b:
        removePackageFromTruck(state, truck_b_index, package_a["id"])

    state["in_trucks"][truck_a]["packages"].append(package_a)
    state["in_trucks"][truck_b_index]["packages"].append(package_b)
    return False

# pilih 1 paket dr truk trs keluarin
def movePackageToWarehouse(state):
    truck_index = chooseRandomSourceTruck(state)
    if truck_index is None:
        return False

    package = random.choice(state["in_trucks"][truck_index]["packages"])
    removePackageFromTruck(state, truck_index, package["id"])
    state["in_warehouse"].append(package["id"])
    return True

# pilih 1 paket dr warehouse trs masukin ke truk
def movePackageFromWarehouse(state):
    if not state["in_warehouse"]:
        return False

    package_id = random.choice(state["in_warehouse"])
    package = getPackageById(package_id)

    possible_trucks = getTrucksWithCapacity(state, package)
    if not possible_trucks:
        return False

    truck_index = random.choice(possible_trucks)

    if tryPlacePackage(state, truck_index, package):
        state["in_warehouse"].remove(package_id)
        return True
    else:
        return False

# ubah posisi 1 paket di truk, oriantasinya tetap
def changePosition(state):
    truck_index = chooseRandomSourceTruck(state)
    if truck_index is None:
        return False

    package = random.choice(state["in_trucks"][truck_index]["packages"])
    package_data = getPackageById(package["id"])
    old_pos = package["position"].copy()

    truck_data = trucks[truck_index]
    dim = getDimensionXYZ({
        "dimension": package_data["dimension"],
        "orientation": package["orientation"]
    })

    # cek apakah paket masih muat
    if (dim["x"] > truck_data["dimension"]["w"] or dim["y"] > truck_data["dimension"]["l"] or dim["z"] > truck_data["dimension"]["h"]):
        return False

    for _ in range(50):
        pos_x = random.randint(0, truck_data["dimension"]["w"] - dim["x"])
        pos_y = random.randint(0, truck_data["dimension"]["l"] - dim["y"])
        pos_z = random.randint(0, truck_data["dimension"]["h"] - dim["z"])

        new_pos = {"x": pos_x, "y": pos_y, "z": pos_z}

        if new_pos == old_pos:
            continue

        package["position"] = new_pos
        return True

    # kalo gagal kembaliin ke posisi sebelumnya
    package["position"] = old_pos
    return False

# # ubah orientasi 1 paket di truk, posisinya tetap
def changeOrientation(state):
    truck_index = chooseRandomSourceTruck(state)
    if truck_index is None:
        return False

    package = random.choice(state["in_trucks"][truck_index]["packages"])
    package_data = getPackageById(package["id"])
    old_orientation = package["orientation"].copy()
    truck_data = trucks[truck_index]

    # enumerate semua kemungkinan orientasi
    orientations = [
        {"w": a, "l": b, "h": c}
        for a, b, c in permutations(["x", "y", "z"])
    ]
    random.shuffle(orientations)

    for new_orientation in orientations:
        # skip orientasi yang sama dgn sekarang
        if new_orientation == old_orientation:
            continue

        dim = getDimensionXYZ({
            "dimension": package_data["dimension"],
            "orientation": new_orientation
        })

        # cek apakah paket masih muat
        if (dim["x"] > truck_data["dimension"]["w"] or dim["y"] > truck_data["dimension"]["l"] or dim["z"] > truck_data["dimension"]["h"]):
            continue

        package["orientation"] = new_orientation
        return True

    # kalo gagal balikin ke orientasi sebelumnya
    package["orientation"] = old_orientation
    return False

# generate neighbor state, ini nanti ditune aja
def generateNeighborState(state, algorithm):
    neighbor_state = deepCopyState(state)

    if algorithm == "HC":
        operations = [movePackageBetweenTrucks, swapPackageBetweenTrucks, movePackageToWarehouse, movePackageFromWarehouse, changePosition, changeOrientation]
        probabilities = [0.2, 0.2, 0.2, 0.2, 0.1, 0.1]
    elif algorithm == "SA":
        operations = [movePackageBetweenTrucks, swapPackageBetweenTrucks, movePackageToWarehouse, movePackageFromWarehouse, changePosition, changeOrientation]
        probabilities = [0.3, 0.3, 0.1, 0.15, 0.075, 0.075]
    elif algorithm == "GA":
        operations = [movePackageBetweenTrucks, swapPackageBetweenTrucks, movePackageToWarehouse, movePackageFromWarehouse, changePosition, changeOrientation]
        probabilities = [0.30, 0.25, 0.10, 0.15, 0.10, 0.10]
    else:
        raise ValueError("Unknown algorithm: {}".format(algorithm))

    operation = random.choices(operations, weights=probabilities)[0]
    success = operation(neighbor_state)

    return neighbor_state if success else state