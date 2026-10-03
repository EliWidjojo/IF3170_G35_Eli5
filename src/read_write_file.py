import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

with open(os.path.join(DATA_DIR, "packages.json"), 'r') as file:
    packages = json.load(file)

with open(os.path.join(DATA_DIR, "trucks.json"), 'r') as file:
    trucks = json.load(file)