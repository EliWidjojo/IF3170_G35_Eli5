from read_write_file import *

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