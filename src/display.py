import os
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from read_write_file import trucks
from helper_function import *
from objective_function import *

FRAGILE_COLOR = "#e63946"
MAX_LABELS = 40
PALETTE = ["#8ecae6", "#a8dadc", "#b7e4c7", "#d8f3dc", "#ffe8a3", "#ffd6a5", "#cdb4db", "#bde0fe", "#c7d3e0", "#e0e1a8", "#b8c0ff", "#9fd8cb"]

#utils

#optional save terus tampilin hasil
def finish(fig, save_path, show):
    if save_path:
        folder = os.path.dirname(save_path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
 
#muka-muka baloknya dengan sudut kiri-bawah-belakang di (x, y, z)
def boxFaces(x, y, z, dx, dy, dz):
    v = [(x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z), (x, y, z + dz), (x + dx, y, z + dz), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)]
    return [
        [v[0], v[1], v[2], v[3]],  
        [v[4], v[5], v[6], v[7]],  
        [v[0], v[1], v[5], v[4]],
        [v[2], v[3], v[7], v[6]],
        [v[1], v[2], v[6], v[5]],
        [v[0], v[3], v[7], v[4]],
    ]
 
#jenis-jenis violations yg ketemu
def violations(state, truck_index):
    found = []
    if isPackageClipping(state, truck_index):
        found.append("clipping")
    if isPackageFlying(state, truck_index):
        found.append("melayang")
    if isFragileBelow(state, truck_index):
        found.append("fragile di bawah")
    if isPackageOutOfBounds(state, truck_index):
        found.append("keluar dari truk")
    return found

def packageViolations(state, truck_index):
    info = {}

    for a, b in getClippingPairs(state, truck_index):
        info.setdefault(a, []).append(f"clipping dgn {b}")
        info.setdefault(b, []).append(f"clipping dgn {a}")

    for pid in getFlyingPackages(state, truck_index):
        info.setdefault(pid, []).append("melayang")

    for pid, fid in getFragileViolations(state, truck_index):
        info.setdefault(pid, []).append(f"di atas fragile {fid}")

    for pid in getOutOfBoundsPackages(state, truck_index):
        info.setdefault(pid, []).append("keluar dari truk")

    return info
 
#mapping warna per id paket biar init dan finalnya mudah dibandingin
def colorMap(state):
    ids = sorted([p["id"] for t in state["in_trucks"] for p in t["packages"]] + list(state["in_warehouse"]))
    return {pid: PALETTE[i % len(PALETTE)] for i, pid in enumerate(ids)}

#garis putus2 ke sumbu xyz
def drawProjectionLines(ax, x, y, z, color="#888888"):
    ax.plot([0, x], [y, y], [z, z], color=color, linewidth=0.4, linestyle="--", alpha=0.5)
    ax.plot([x, x], [0, y], [z, z], color=color, linewidth=0.4, linestyle="--", alpha=0.5)
    ax.plot([x, x], [y, y], [0, z], color=color, linewidth=0.4, linestyle="--", alpha=0.5)

#3d crates
def drawTruckkun(ax, truck_index, state, colors, labels=False):
    truck_data = trucks[truck_index]
    W, L, H = (truck_data["dimension"][k] for k in ("w", "l", "h"))
    placed = state["in_trucks"][truck_index]["packages"]
    #kerangka petinya
    ax.add_collection3d(Poly3DCollection(boxFaces(0, 0, 0, W, L, H), facecolors=(0, 0, 0, 0), edgecolors="#555555", linewidths=1.2))
    for sp in placed:
        pkg = getPackageById(sp["id"])
        dim = getDimensionXYZ({
            "dimension": pkg["dimension"],
            "orientation": sp["orientation"]
        })
        pos = sp["position"]
        fragile = pkg["isFragile"]
        ax.add_collection3d(
            Poly3DCollection(
                boxFaces(pos["x"], pos["y"], pos["z"], dim["x"], dim["y"], dim["z"]),
                facecolors=FRAGILE_COLOR if fragile else colors[sp["id"]],
                edgecolors="#7a0011" if fragile else "#333333",
                linewidths=1.0 if fragile else 0.5, alpha=0.85,
            )
        )
        drawProjectionLines(ax, pos["x"], pos["y"], pos["z"])
        if labels and len(placed) <= MAX_LABELS:
            ax.text(pos["x"] + dim["x"] / 2, pos["y"] + dim["y"] / 2, pos["z"] + dim["z"], sp["id"], fontsize=6, ha="center", va="bottom")

    # grid lantai
    for gx in range(0, W + 1, 2):
        ax.plot([gx, gx], [0, L], [0, 0], color="#dddddd", linewidth=0.3, alpha=0.35)
    for gy in range(0, L + 1, 5):
        ax.plot([0, W], [gy, gy], [0, 0], color="#dddddd", linewidth=0.3, alpha=0.35)

    # grid dinding belakang
    for gx in range(0, W + 1, 2):
        ax.plot([gx, gx], [L, L], [0, H], color="#dddddd", linewidth=0.3, alpha=0.35)
    for gz in range(0, H + 1, 1):
        ax.plot([0, W], [L, L], [gz, gz], color="#dddddd", linewidth=0.3, alpha=0.35)

    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    ax.set_zlim(0, H)
    ax.set_box_aspect((W, L, H))
    ax.set_xticks(range(0, W + 1, 2))
    ax.set_yticks(range(0, L + 1, 5))
    ax.set_zticks(range(0, H + 1))
    ax.tick_params(labelsize=7)
    ax.set_xlabel("x (w)", fontsize=8)
    ax.set_ylabel("y (l)", fontsize=8)
    ax.set_zlabel("z (h)", fontsize=8)
    ax.view_init(elev=26, azim=-28)
    ax.set_title(f"{state['in_trucks'][truck_index]['truck']}  ({len(placed)} paket)", fontsize=10)

def infoState(state):
    lines = []
    tot_val = 0
    for i, t in enumerate(state["in_trucks"]):
        value = calculateTruckValue(state, i)
        weight = calculateTruckWeight(state, i)
        cap = trucks[i]["max_capacity"]
        bad = violations(state, i)
        tot_val += value
        lines.append(f"[{t['truck']}] value={value}  berat={weight}/{cap}")
        lines.append("   constraint: " + ("OK" if not bad else "MELANGGAR -> " + ", ".join(bad)))
    lines.insert(0, f"TOTAL VALUE di truk : {tot_val}")
    lines.insert(1, "")
 
    lines.append("")
    lines.append("DI DALAM PETI KEMAS (id: x,y,z | w x l x h [orientasi])")
    for ti, t in enumerate(state["in_trucks"]):
        bad = packageViolations(state, ti)
        lines.append(f"  --- {t['truck']} ({len(t['packages'])} paket) ---")
        for sp in t["packages"]:
            pkg = getPackageById(sp["id"])
            d = getDimensionXYZ({
                "dimension": pkg["dimension"],
                "orientation": sp["orientation"]
            })
            p = sp["position"]
            o = sp["orientation"]
            tag = " *fragile" if pkg["isFragile"] else ""
            mark = ""
            if sp["id"] in bad:
                mark = "  <-- " + ", ".join(bad[sp["id"]])
            lines.append(
                f"    {sp['id']}: {p['x']},{p['y']},{p['z']} | {d['x']}x{d['y']}x{d['z']} "
                f"[{o['w']}{o['l']}{o['h']}] v={pkg['value']}{tag}{mark}"
            )
    lines.append("")
    lines.append(f"DI LUAR / GUDANG ({len(state['in_warehouse'])} paket)")
    outside = []
    for pid in state["in_warehouse"]:
        pkg = getPackageById(pid)
        d = pkg["dimension"]
        tag = " *fragile" if pkg["isFragile"] else ""
        outside.append(f"{pid}: {d['w']}x{d['l']}x{d['h']} v={pkg['value']} berat={pkg['weight']}{tag}")
    lines += outside if outside else ["(kosong)"]
    return "\n".join(lines)

#tampilin kondisi suatu state -> tiap crate in 3d + panel teks
def showState(state, title="State", save_path=None, show=True, labels=False):
    n = len(state["in_trucks"])
    colors = colorMap(state)
    info = infoState(state)
    height = max(7, 0.125 * (info.count("\n") + 1) + 1)  
    fig = plt.figure(figsize=(6.5 * n + 6, height))
    gs = fig.add_gridspec(1, n + 1, width_ratios=[3] * n + [2.6])
    for i in range(n):
        ax = fig.add_subplot(gs[0, i], projection="3d")
        drawTruckkun(ax, i, state, colors, labels)
    ax_text = fig.add_subplot(gs[0, n])
    ax_text.axis("off")
    ax_text.text(0.1, 1, info, va="top", ha="left", family="monospace", fontsize=7)
    fig.legend(
        handles=[Patch(facecolor=FRAGILE_COLOR, edgecolor="black", label="fragile"),
                 Patch(facecolor=PALETTE[0], edgecolor="black", label="regular")],
        loc="lower left", fontsize=8,
    )
    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    finish(fig, save_path, show)

def plotHC(results, save_path=None, show=True, title="Algorithm"):
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])
    
    ax_obj = fig.add_subplot(gs[0, 0])
    ax_tab = fig.add_subplot(gs[1, 0])

    # plot cost vs iterasi
    for i, r in enumerate(results):
        history = r.get("costHistory", [])
        ax_obj.plot(
            range(len(history)),
            history,
            linewidth=1.5,
            label=f"Run {i + 1}"
        )

    ax_obj.set_xlabel("Iterasi")
    ax_obj.set_ylabel("Cost")
    ax_obj.grid(alpha=0.3)
    if len(results) > 0:
        ax_obj.legend()

    # tabel ringkasan
    ax_tab.axis("off")
    
    headers = ["Run", "Value", "Cost", "Durasi", "Iterasi"]
    keys = ["finalVal", "finalCost", "duration", "iterations"]
    
    if any("sideWaysMoves" in r for r in results):
        headers.append("Sideways Moves")
        keys.append("sideWaysMoves")
        
    if any("restarts" in r for r in results):
        headers.append("Restarts")
        keys.append("restarts")
        
    if any("iterationsPerRestart" in r for r in results):
        headers.append("Avg Iter/Restart")
        keys.append("iterationsPerRestart")

    rows = []
    for i, r in enumerate(results):
        row = [f"Run {i+1}"]
        for k in keys:
            val = r.get(k, "-")
            
            if k == "duration":
                row.append(f"{val:.1f}s" if isinstance(val, (int, float)) else val)
            elif k == "iterationsPerRestart":
                if isinstance(val, list) and len(val) > 0:
                    avg = sum(val) / len(val)
                    row.append(f"{avg:.1f}")
                else:
                    row.append("-")
            else:
                row.append(str(val))
        rows.append(row)

    table = ax_tab.table(
        cellText=rows, 
        colLabels=headers, 
        loc="center", 
        cellLoc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(list(range(len(headers))))
    table.scale(1, 1.8)

    fig.suptitle(title, fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    finish(fig, save_path, show)

#list result dict dari sim anneal -> panel cost vs iterasi, e^(dE/T) vs iterasi, frekuensi stuck, tabel ringkasan
def plotSA(results, save_path=None, show=True):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    ax_obj, ax_prob, ax_stuck, ax_tab = axes.flatten()

    for i, r in enumerate(results):
        ax_obj.plot(
            r["costHistory"],
            linewidth=1,
            label=f"Run {i + 1}"
        )

        probs = r.get("probabilityHistory", [])
        if probs:
            xs = [p[0] for p in probs]
            ys = [p[1] for p in probs]
            ax_prob.scatter(xs, ys, s=4, alpha=0.35, label=f"Run {i + 1}")

    ax_obj.set_title("Objective terhadap iterasi")
    ax_obj.set_xlabel("iterasi")
    ax_obj.set_ylabel("value")
    ax_obj.grid(alpha=0.3)
    ax_obj.legend()

    ax_prob.set_title("Probabilitas menerima move yang lebih buruk")
    ax_prob.set_xlabel("iterasi")
    ax_prob.set_ylabel("e^(ΔE/T)")
    ax_prob.set_ylim(-0.02, 1.02)
    ax_prob.grid(alpha=0.3)
    if ax_prob.get_legend_handles_labels()[0]:
        ax_prob.legend(markerscale=3)

    labels = [f"Run {i + 1}" for i in range(len(results))]
    stuck = [r.get("stuckCtr", 0) for r in results]
    bars = ax_stuck.bar(labels, stuck)
    ax_stuck.bar_label(bars)
    ax_stuck.set_title("Frekuensi move lebih buruk yang ditolak")
    ax_stuck.set_ylabel("jumlah")
    ax_stuck.grid(axis="y", alpha=0.3)

    ax_tab.axis("off")
    rows = []
    for i, r in enumerate(results):
        rows.append([
            f"Run {i + 1}",
            r.get("seed", "-"),
            r.get("iterations", len(r["costHistory"]) - 1),
            r["finalVal"],
            f"{r['duration']:.1f}",
            r.get("stuckCtr", "-"),
            r.get("failedCtr", "-")
        ])

    table = ax_tab.table(
        cellText=rows,
        colLabels=["Run", "Seed", "Iterasi", "Value akhir", "Durasi (s)", "Stuck", "Move gagal"],
        loc="center",
        cellLoc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.auto_set_column_width(list(range(7)))
    table.scale(1, 1.8)
    ax_tab.set_title("Ringkasan eksperimen")

    fig.suptitle("Simulated Annealing", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    finish(fig, save_path, show)

def plotGA(results, save_path=None, show=True):
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, res in enumerate(results, 1):
        best_history = res["costHistory"]
        avg_history = res["avgCostHistory"]

        iterations = range(len(best_history))

        # Biaya terbaik pada setiap generasi
        ax.plot(
            iterations,
            best_history,
            linestyle="-",
            alpha=0.85,
            label=f"Best Cost - Run {i}"
        )

        # Biaya rata-rata seluruh populasi
        ax.plot(
            range(len(avg_history)),
            avg_history,
            linestyle="--",
            alpha=0.55,
            label=f"Average Cost - Run {i}"
        )

    ax.set_title("Genetic Algorithm: Objective per Generation")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Cost (lower is better)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    if save_path:
        os.makedirs(
            os.path.dirname(save_path) or ".",
            exist_ok=True
        )
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    plt.close(fig)

