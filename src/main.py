import os, glob, json, random, time
from read_write_file import *
from sim_anneal import *
from hill_climbing import *
from genetic_algorithm import *
import display

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SHOW_WINDOWS = True #kalau false, gambarnya cuman disave jadi png, ga ditampilin

ALGOS = { #file name, display name, func, ma func plot hasil
    "1": ("HC-SA", "Hill Climbing Steepest Ascent", hillClimbing, display.plotSA),
    "2": ("HC-SM", "Hill Climbing with Sideways Move", sideWaysHillClimbing, display.plotSA),
    "3": ("HC-S", "Stochastic Hill Climbing", stochasticHillClimbing, display.plotSA),
    "4": ("HC-RR", "Random Restart Hill Climbing", randomRestartHillClimbing, display.plotSA),
    "5": ("SA", "Simulated Annealing", simulatedAnnealing, display.plotSA),
    "6": ("GA", "Genetic Algorithm", geneticAlgorithm, display.plotGA)
    #tambahin yang lain yaw
}

#simpan/baca hasil
def resPath(name):
    return os.path.join(OUTPUT_DIR, f"{name}.json")

def clearRes(name):
    for path in glob.glob(os.path.join(OUTPUT_DIR, f"{name}_run*.json")):
        os.remove(path)

def saveRes(name, res):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(resPath(name), "w") as f:
        json.dump(res, f, indent=2)

def loadRes(name):
    with open(resPath(name), "r") as f:
        return json.load(f)

#jalankan dan tampilkan
def runSAExperiment(name, label, algo):
    clearRes(name)

    seed = random.randrange(1, 1000000)
    random.seed(seed)
 
    start_time = time.perf_counter()
    finalState, finalCost, costHistory, initState, probabilityHistory, stuckCtr, failedCtr, iters = algo()
    duration = time.perf_counter() - start_time
    res = {
        "initState": initState,
        "finalState": finalState,
        "finalCost": finalCost,
        "finalVal": calculateTotVal(finalState),
        "costHistory": costHistory,
        "seed": seed,
        "duration": duration,
        "probabilityHistory": probabilityHistory,
        "stuckCtr": stuckCtr,
        "failedCtr": failedCtr,
        "iterations": iters
    }
    saveRes(name, res)

    info_init = display.infoState(initState)
    info_final = display.infoState(finalState)
    info_path = os.path.join(OUTPUT_DIR, f"{name}_info.txt")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"(seed={seed}) ===\n")
        f.write(f"value akhir = {res['finalVal']} | cost = {res['finalCost']} | durasi = {res['duration']:.1f}s\n\n")
        f.write("### INITIAL STATE ###\n")
        f.write(info_init + "\n\n")
        f.write("### FINAL STATE ###\n")
        f.write(info_final + "\n")

    print(f"    value di truk = {res['finalVal']}"
            f" | cost = {res['finalCost']}"
            f" | durasi = {res['duration']:.1f}s")
    print(f"    info disimpan di: {info_path}")

    return res


def runGAExperiment(name, label, algo, populationSize, generations):
    clearRes(name)

    seed = random.randrange(1, 1000000)
    random.seed(seed)

    start_time = time.perf_counter()

    (
        finalState,
        finalCost,
        costHistory,
        initState,
        avgCostHistory,
        iters
    ) = algo(
        populationSize=populationSize,
        generations=generations
    )

    duration = time.perf_counter() - start_time

    res = {
        "initState": initState,
        "finalState": finalState,
        "finalCost": finalCost,
        "finalVal": calculateTotVal(finalState),
        "costHistory": costHistory,
        "avgCostHistory": avgCostHistory,
        "populationSize": populationSize,
        "generations": generations,
        "iterations": iters,
        "seed": seed,
        "duration": duration
    }

    saveRes(name, res)

    info_init = display.infoState(initState)
    info_final = display.infoState(finalState)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    info_path = os.path.join(
        OUTPUT_DIR,
        f"{name}_info.txt"
    )

    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"(seed={seed}) ===\n")
        f.write(f"Populasi = {populationSize}\n")
        f.write(f"Jumlah generasi = {iters}\n")
        f.write(f"value akhir = {res['finalVal']} | cost = {res['finalCost']} | durasi = {res['duration']:.1f}s\n\n")

        f.write("### INITIAL STATE ###\n")
        f.write(info_init + "\n\n")

        f.write("### FINAL STATE ###\n")
        f.write(info_final + "\n")


    print(
        f"    Value di truk = {res['finalVal']} "
        f"| Cost = {finalCost} "
        f"| Durasi = {duration:.1f}s"
    )
    print(f"    Info disimpan di: {info_path}")

    return res

def showResults(name, label, result, plotFunc):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    display.showState(
        result["initState"],
        f"{label} - initial state",
        save_path=os.path.join(OUTPUT_DIR, f"{name}_initial.png"),
        show=SHOW_WINDOWS
    )

    display.showState(
        result["finalState"],
        f"{label} - final state",
        save_path=os.path.join(OUTPUT_DIR, f"{name}_final.png"),
        show=SHOW_WINDOWS
    )

    plotFunc(
        [result],
        save_path=os.path.join(OUTPUT_DIR, f"{name}_plot.png"),
        show=SHOW_WINDOWS
    )

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
            if choice == "1-4":
                print("Test")
            elif choice == "5":
                results = runSAExperiment(name, label, algo)
            elif choice == "6":
                try:
                    populationSize = int(input("Ukuran populasi [default: 100]: ").strip())
                    generations = int(input("Jumlah generasi [default: 100]: ").strip())

                    if populationSize < 5 or generations < 1:
                        print("Populasi minimal 5 dan generasi minimal 1")
                        continue

                except ValueError:
                    print("Masukkan angka bulat yang valid.")
                    continue

                results = runGAExperiment(name, label, algo, populationSize=populationSize, generations=generations)
                 
        showResults(name, label, results, plotFunc)
 
if __name__ == "__main__":
    main()