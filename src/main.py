import os, glob, json, random, time
from read_write_file import *
from sim_anneal import *
from hill_climbing import *
from genetic_algorithm import *
import display

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SHOW_WINDOWS = True #kalau false, gambarnya cuman disave jadi png, ga ditampilin

ALGOS = { #file name, display name, func, ma func plot hasil
    "1": ("HC-SA", "Hill Climbing Steepest Ascent", steepestAscentHillClimbing, display.plotHC),
    "2": ("HC-SM", "Hill Climbing with Sideways Move", sideWaysHillClimbing, display.plotHC),
    "3": ("HC-S", "Stochastic Hill Climbing", stochasticHillClimbing, display.plotHC),
    "4": ("HC-RR", "Random Restart Hill Climbing", randomRestartHillClimbing, display.plotHC),
    "5": ("SA", "Simulated Annealing", simulatedAnnealing, display.plotSA),
    "6": ("GA", "Genetic Algorithm", geneticAlgorithm, display.plotGA)
    #tambahin yang lain yaw
}

#simpan/baca hasil
def get_run_dir(name, run):
    path = os.path.join(OUTPUT_DIR, f"{name}_run{run}")
    os.makedirs(path, exist_ok=True)
    return path

def get_next_run(name):
    if not os.path.exists(OUTPUT_DIR):
        return 1
    runs = [0]
    for f in os.listdir(OUTPUT_DIR):
        if f.startswith(f"{name}_run"):
            try:
                num = int(f.split("_run")[1])
                runs.append(num)
            except:
                pass
    return max(runs) + 1

def saveRes(name, run, res):
    folder = get_run_dir(name, run)
    path = os.path.join(folder, f"{name}.json")
    with open(path, "w") as f:
        json.dump(res, f, indent=2)

def loadRes(name, run):
    path = os.path.join(OUTPUT_DIR, f"{name}_run{run}", f"{name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

#jalankan dan tampilkan
def runHCSteepestExperiment(name, label, algo, run):
    seed = random.randrange(1, 1000000)
    random.seed(seed)

    start_time = time.perf_counter()
    finalState, finalCost, costHistory, initState, iters = algo()
    duration = time.perf_counter() - start_time
    res = {
        "initState": initState,
        "finalState": finalState,
        "finalCost": finalCost,
        "finalVal": calculateTotVal(finalState),
        "costHistory": costHistory,
        "seed": seed,
        "duration": duration,
        "iterations": iters
    }
    saveRes(name, run, res)

    info_init = display.infoState(initState)
    info_final = display.infoState(finalState)
    folder = get_run_dir(name, run)
    info_path = os.path.join(folder, f"{name}_info.txt")
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"(seed={seed}) ===\n")
        f.write(f"Jumlah iterasi = {res['iterations']}\n")
        f.write(f"value akhir = {res['finalVal']} | cost = {res['finalCost']} | durasi = {res['duration']:.1f}s\n\n")
        f.write("### INITIAL STATE ###\n")
        f.write(info_init + "\n\n")
        f.write("### FINAL STATE ###\n")
        f.write(info_final + "\n")

    print(f"    value di truk = {res['finalVal']}"
            f" | cost = {res['finalCost']}"
            f" | durasi = {res['duration']:.1f}s"
            f" | iterasi = {res['iterations']}")
    print(f"    info disimpan di: {info_path}")

    return res

def runHCSidewaysExperiment(name, label, algo, run, max_sm=10):
    seed = random.randrange(1, 1000000)
    random.seed(seed)

    start_time = time.perf_counter()
    finalState, finalCost, costHistory, initState, iters, sideWaysMoves = algo(maxSideWaysMoves=max_sm)
    duration = time.perf_counter() - start_time
    res = {
        "initState": initState,
        "finalState": finalState,
        "finalCost": finalCost,
        "finalVal": calculateTotVal(finalState),
        "costHistory": costHistory,
        "seed": seed,
        "duration": duration,
        "iterations": iters,
        "sideWaysMoves": sideWaysMoves,
        "maxSideWaysMoves": max_sm
    }
    saveRes(name, run, res)

    info_init = display.infoState(initState)
    info_final = display.infoState(finalState)
    folder = get_run_dir(name, run)
    info_path = os.path.join(folder, f"{name}_info.txt")
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"(seed={seed}) ===\n")
        f.write(f"Jumlah iterasi = {res['iterations']}\n")
        f.write(f"Jumlah side ways moves = {res['sideWaysMoves']} | max side ways moves = {res['maxSideWaysMoves']}\n")
        f.write(f"value akhir = {res['finalVal']} | cost = {res['finalCost']} | durasi = {res['duration']:.1f}s\n\n")
        f.write("### INITIAL STATE ###\n")
        f.write(info_init + "\n\n")
        f.write("### FINAL STATE ###\n")
        f.write(info_final + "\n")

    print(f"    value di truk = {res['finalVal']}"
            f" | cost = {res['finalCost']}"
            f" | durasi = {res['duration']:.1f}s"
            f" | iterasi = {res['iterations']}"
            f" | sideways moves dilakukan = {res['sideWaysMoves']}"
            f" | max side ways moves = {res['maxSideWaysMoves']}")
    print(f"    info disimpan di: {info_path}")

    return res

def runHCStochasticExperiment(name, label, algo, run):    
    seed = random.randrange(1, 1000000)
    random.seed(seed)

    start_time = time.perf_counter()
    finalState, finalCost, costHistory, initState, iters = algo()
    duration = time.perf_counter() - start_time
    res = {
        "initState": initState,
        "finalState": finalState,
        "finalCost": finalCost,
        "finalVal": calculateTotVal(finalState),
        "costHistory": costHistory,
        "seed": seed,
        "duration": duration,
        "iterations": iters
    }
    saveRes(name, run, res)

    info_init = display.infoState(initState)
    info_final = display.infoState(finalState)
    folder = get_run_dir(name, run)
    info_path = os.path.join(folder, f"{name}_info.txt")
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"(seed={seed}) ===\n")
        f.write(f"Jumlah iterasi = {res['iterations']}\n")
        f.write(f"value akhir = {res['finalVal']} | cost = {res['finalCost']} | durasi = {res['duration']:.1f}s\n\n")
        f.write("### INITIAL STATE ###\n")
        f.write(info_init + "\n\n")
        f.write("### FINAL STATE ###\n")
        f.write(info_final + "\n")

    print(f"    value di truk = {res['finalVal']}"
            f" | cost = {res['finalCost']}"
            f" | durasi = {res['duration']:.1f}s"
            f" | iterasi = {res['iterations']}")
    print(f"    info disimpan di: {info_path}")

    return res

def runHCRandomRestartExperiment(name, label, algo, run, max_rr=10):
    seed = random.randrange(1, 1000000)
    random.seed(seed)

    start_time = time.perf_counter()
    finalState, finalCost, costHistory, initState, itersPerRestart, restarts, totalIters = algo(maxRestarts=max_rr)
    duration = time.perf_counter() - start_time
    res = {
        "initState": initState,
        "finalState": finalState,
        "finalCost": finalCost,
        "finalVal": calculateTotVal(finalState),
        "costHistory": costHistory,
        "seed": seed,
        "duration": duration,
        "iterations": totalIters,
        "iterationsPerRestart": itersPerRestart,
        "restarts": restarts,
        "maxRestarts": max_rr
    }
    saveRes(name, run, res)

    info_init = display.infoState(initState)
    info_final = display.infoState(finalState)
    folder = get_run_dir(name, run)
    info_path = os.path.join(folder, f"{name}_info.txt")
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"(seed={seed}) ===\n")
        f.write(f"Iterasi per restart = {res['iterationsPerRestart']}\n")
        f.write(f"Jumlah restart = {res['restarts']}\n")
        f.write(f"Total iterasi = {res['iterations']}\n")
        f.write(f"value akhir = {res['finalVal']} | cost = {res['finalCost']} | durasi = {res['duration']:.1f}s\n\n")
        f.write("### INITIAL STATE ###\n")
        f.write(info_init + "\n\n")
        f.write("### FINAL STATE ###\n")
        f.write(info_final + "\n")

    print(f"    value di truk = {res['finalVal']}"
            f" | cost = {res['finalCost']}"
            f" | durasi = {res['duration']:.1f}s"
            f" | iterasi per restart = {res['iterationsPerRestart']}"
            f" | total iterasi = {res['iterations']}"
            f" | jumlah restart = {res['restarts']}")
    print(f"    info disimpan di: {info_path}")

    return res

def runSAExperiment(name, label, algo, run):
    seed = random.randrange(1, 1000000)
    random.seed(seed)
 
    start_time = time.perf_counter()
    finalState, finalCost, costHistory, initState, probabilityHistory, rejectedWorseMoves, iters = algo()
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
        "rejectedWorseMoves": rejectedWorseMoves,
        "iterations": iters
    }
    saveRes(name, run, res)

    info_init = display.infoState(initState)
    info_final = display.infoState(finalState)
    folder = get_run_dir(name, run)
    info_path = os.path.join(folder, f"{name}_info.txt")
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"(seed={seed}) ===\n")
        f.write(f"Frekuensi stuck di local optimum (asumsinya itu berapa kali dia reject worser moves) = {res['rejectedWorseMoves']}\n")
        f.write(f"value akhir = {res['finalVal']} | cost = {res['finalCost']} | durasi = {res['duration']:.1f}s\n\n")
        f.write("### INITIAL STATE ###\n")
        f.write(info_init + "\n\n")
        f.write("### FINAL STATE ###\n")
        f.write(info_final + "\n")

    print(f"    value di truk = {res['finalVal']}"
            f" | cost = {res['finalCost']}"
            f" | durasi = {res['duration']:.1f}s"
            f" | frekuensi stuck di local optimum (asumsinya itu berapa kali dia reject worser moves) = {res['rejectedWorseMoves']}")
    print(f"    info disimpan di: {info_path}")

    return res


def runGAExperiment(name, label, algo, run, populationSize, generations):
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

    saveRes(name, run, res)

    info_init = display.infoState(initState)
    info_final = display.infoState(finalState)

    folder = get_run_dir(name, run)
    info_path = os.path.join(folder, f"{name}_info.txt")

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

def showResults(name, label, result, run, plotFunc):
    folder = get_run_dir(name, run)
    
    display.showState(
        result["initState"], f"{label} - Run {run} - Initial", 
        save_path=os.path.join(folder, "initial.png"), show=SHOW_WINDOWS
    )
    display.showState(
        result["finalState"], f"{label} - Run {run} - Final", 
        save_path=os.path.join(folder, "final.png"), show=SHOW_WINDOWS
    )

    plotFunc(
        [result],
        save_path=os.path.join(folder, "plot.png"),
        show=SHOW_WINDOWS, title=f"{label} - Run {run}"
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
            try:
                run_num = int(input("Mau load Run ke berapa? "))
                result = loadRes(name, run_num)
                if not result:
                    print(f"Hasil Run {run_num} untuk {label} tidak ditemukan.")
                    continue
                showResults(name, label, result, run_num, plotFunc)
            except ValueError:
                print("Masukkan angka run yang valid.")
            continue

        run_num = get_next_run(name)
        
        params = {}
        if choice == "2":
            while True:
                try:
                    val = input("Max Sideways Moves [default: 10]: ").strip()
                    params["max_sm"] = int(val) if val else 10
                    if params["max_sm"] <= 0:
                        print("Angka harus lebih dari 0")
                        continue
                    break
                except ValueError:
                    print("Input tidak valid! Masukkan angka.")
        elif choice == "4":
            while True:
                try:
                    val = input("Max Restarts [default: 10]: ").strip()
                    params["max_rr"] = int(val) if val else 10
                    if params["max_rr"] <= 0:
                        print("Angka harus lebih dari 0")
                        continue
                    break
                except ValueError:
                    print("Input tidak valid! Masukkan angka.")
        elif choice == "6":
            while True:
                try:
                    p = input("Ukuran populasi [default: 100]: ").strip()
                    g = input("Jumlah generasi [default: 100]: ").strip()
                    params["populationSize"] = int(p) if p else 100
                    params["generations"] = int(g) if g else 100
                    if params["populationSize"] < 5 or params["generations"] < 1:
                        print("Populasi minimal 5 dan generasi minimal 1. Coba lagi.")
                        continue
                    break
                except ValueError:
                    print("Input tidak valid! Masukkan angka.")

        if choice == "1": result = runHCSteepestExperiment(name, label, algo, run_num)
        elif choice == "2": result = runHCSidewaysExperiment(name, label, algo, run_num, **params)
        elif choice == "3": result = runHCStochasticExperiment(name, label, algo, run_num)
        elif choice == "4": result = runHCRandomRestartExperiment(name, label, algo, run_num, **params)
        elif choice == "5": result = runSAExperiment(name, label, algo, run_num)
        elif choice == "6": result = runGAExperiment(name, label, algo, run_num, **params)
             
        showResults(name, label, result, run_num, plotFunc)
 
if __name__ == "__main__":
    main()