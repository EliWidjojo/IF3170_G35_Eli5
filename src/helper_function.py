from read_write_file import *
import copy

def getPackageById(id):
    for package in packages:
        if package["id"] == id:
            return package
    return None

def getDimensionXYZ(package):
    dimension = package["dimension"]
    orientation = package["orientation"]

    dimension_xyz = {
        "x": 0,
        "y": 0,
        "z": 0
    }

    dimension_xyz[orientation["w"]] = dimension["w"]
    dimension_xyz[orientation["l"]] = dimension["l"]
    dimension_xyz[orientation["h"]] = dimension["h"]

    return dimension_xyz

def getPackagePlacement(state, package_id):
    if package_id in state["in_warehouse"]:
        return {
            "location": "warehouse",
            "package": package_id
        }

    for truck in state["in_trucks"]:
        for package in truck["packages"]:
            if package["id"] == package_id:
                return {
                    "location": "truck",
                    "truck": truck["truck"],
                    "package": package
                }

    return None