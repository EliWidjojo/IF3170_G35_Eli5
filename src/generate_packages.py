import json
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def createPackages(k):
    packages = []

    for i in range(k):
        axes = random.sample(["x", "y", "z"], 3)
        packages.append({
            "id": i,
            "dimension": 
            {
                "w": random.randint(1, 10),
                "l": random.randint(1, 10),
                "h": random.randint(1, 10)
            },
            "orientation": {
                "w": axes[0],
                "l": axes[1],
                "h": axes[2]
            },
            "value": random.randint(20, 100),
            "weight": random.randint(5, 20),
            "isFragile": bool(random.getrandbits(1)),
            "eta": random.randint(1, 5)  
        })

    with open(os.path.join(DATA_DIR, "packages.json"), 'w') as f:
        json.dump(packages, f, indent=4)

    print("Created Packages!")

k = int(input("Masukkan jumlah: "))
createPackages(k)

