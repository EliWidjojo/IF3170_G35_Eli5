import os, glob, json, random
from read_write_file import *
from sim_anneal import *
from hill_climbing import *
import display

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
RUNS = 3
SHOW_WINDOWS = True #kalau false, gambarnya cuman disave jadi png, ga ditampilin

ALGOS = { #file name, display name, func, ma func plot hasil
    "1": ("HC-SA", "Hill Climbing Steepest Ascent", hillClimbing, display.plotSA),
    "2": ("HC-SM", "Hill Climbing with Sideways Move", sideWaysHillClimbing, display.plotSA),
    "3": ("HC-S", "Stochastic Hill Climbing", stochasticHillClimbing, display.plotSA),
    "4": ("HC-RR", "Random Restart Hill Climbing", randomRestartHillClimbing, display.plotSA),
    "5": ("SA", "Simulated Annealing", simulatedAnnealing, display.plotSA),
    "6": ("GA", "Genetic Algorithm", simulatedAnnealing, display.plotSA)
    #tambahin yang lain yaw
}

#simpan/baca hasil
def resPath(name, run):
    return os.path.join(OUTPUT_DIR, f"{name}_run{run}.json")

def clearRes(name):
    for path in glob.glob(os.path.join(OUTPUT_DIR, f"{name}_run*.json")):
        os.remove(path)

def saveRes(name, run, res):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(resPath(name, run), "w") as f:
        json.dump(res, f, indent=2)

def loadRes(name):
    res = []
    run = 1
    while os.path.exists(resPath(name, run)):
        with open(resPath(name, run), "r") as f:
            res.append(json.load(f))
        run += 1
    return res

#jalankan dan tampilkan
def runExperiment(name, label, algo):
    clearRes(name)
    results = []

    for run in range(1, RUNS + 1):
        seed = random.randrange(1, 1000000)
        random.seed(seed)
        print(f"[{label}] run {run}/{RUNS} (seed={seed}) ...")
        start_time = time.perf_counter()
        finalState, finalCost, costHistory, initState = algo()
        duration = time.perf_counter() - start_time
        res = {
            "initState": initState,
            "finalState": finalState,
            "finalCost": finalCost,
            "finalVal": calculateTotVal(finalState),
            "costHistory": costHistory,
            "seed": seed,
            "duration": duration
        }
        saveRes(name, run, res)
        results.append(res)
        print(f"    value di truk = {res['finalVal']}"
              f" | cost = {res['finalCost']}"
              f" | durasi = {res['duration']:.1f}s")

    return results

def showResults(name, label, results, plotFunc):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, r in enumerate(results, 1):
        display.showState(
            r["initState"],
            f"{label} - run {i} - initial state",
            save_path=os.path.join(OUTPUT_DIR, f"{name}_run{i}_initial.png"),
            show=SHOW_WINDOWS
        )
        display.showState(
            r["finalState"],
            f"{label} - run {i} - final state",
            save_path=os.path.join(OUTPUT_DIR, f"{name}_run{i}_final.png"),
            show=SHOW_WINDOWS
        )

    plotFunc(results, save_path=os.path.join(OUTPUT_DIR, f"{name}_plot.png"), show=SHOW_WINDOWS)

def main():
    while True:
        print("\n=== Mejiro Express - Local Search ===")
        for code, (_, label, _, _) in ALGOS.items():
            print(f"{code}. {label}")
        print("0. Keluar")
 
        choice = input("Pilih algoritma: ").strip()
        if choice == "0":
            break
        if choice not in ALGOS:
            print("Pilihan tidak dikenal.")
            continue
        name, label, algo, plotFunc = ALGOS[choice]
 
        mode = input("(r)un baru atau (l)oad hasil dari output? [r/l]: ").strip().lower()
        if mode == "l":
            results = loadRes(name)
            if not results:
                print(f"Belum ada hasil tersimpan untuk {label}. Jalankan dulu dengan 'r'.")
                continue
        else:
            results = runExperiment(name, label, algo)
 
        showResults(name, label, results, plotFunc)
 
 
if __name__ == "__main__":
    main()