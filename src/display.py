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
    lines = info.split("\n")
    max_line_len = max(len(line) for line in lines)
    height = max(8, 0.20 * len(lines) + 1)
    text_width = max(4.5, min(8, max_line_len * 0.075)) 
    fig = plt.figure(
        figsize=(6.5 * n + text_width, height)
    )

    gs = fig.add_gridspec(
        1, n + 1,
        width_ratios=[3] * n + [text_width / 2]
    )
    for i in range(n):
        ax = fig.add_subplot(gs[0, i], projection="3d")
        drawTruckkun(ax, i, state, colors, labels)
    ax_text = fig.add_subplot(gs[0, n])
    ax_text.axis("off")
    ax_text.text(0, 1, info, va="top", ha="left", family="monospace", fontsize=7, transform=ax_text.transAxes, wrap=True)
    fig.legend(
        handles=[Patch(facecolor=FRAGILE_COLOR, edgecolor="black", label="fragile"),
                    *[
                        Patch(facecolor=color, edgecolor="black", label="regular")
                        for i, color in enumerate(PALETTE)
                    ],
                ],
        loc="lower left", fontsize=8,
    )
    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    finish(fig, save_path, show)

def plotHC(results, save_path=None, show=True, title="Algorithm"):
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])
    
    ax_cost = fig.add_subplot(gs[0, 0])
    ax_tab = fig.add_subplot(gs[1, 0])

    # plot cost vs iterasi
    for i, r in enumerate(results):
        history = r.get("costHistory", [])
        ax_cost.plot(
            range(len(history)),
            history,
            linewidth=1.5,
        )

    ax_cost.set_xlabel("Iterasi")
    ax_cost.set_ylabel("Cost")
    ax_cost.grid(alpha=0.3)

    # tabel ringkasan
    ax_tab.axis("off")
    r = results[0]

    headers = ["Value", "Cost", "Durasi", "Iterasi"]
    values = [
        str(r.get("finalVal", "-")),
        str(r.get("finalCost", "-")),
        f"{r.get('duration', 0):.1f}s",
        str(r.get("iterations", "-"))
    ]
    
    if "sideWaysMoves" in r:
        headers.append("Sideways Moves")
        values.append(str(r.get("sideWaysMoves", "-")))
        headers.append("Max Sideways Moves")
        values.append(str(r.get("maxSideWaysMoves", "-")))
        
    if "restarts" in r:
        headers.append("Restarts")
        values.append(str(r.get("restarts", "-")))

    if "iterationsPerRestart" in r:
        headers.append("Avg Iter/Restart")
        val = r.get("iterationsPerRestart", [])
        if isinstance(val, list) and len(val) > 0:
            avg = sum(val) / len(val)
            values.append(f"{avg:.1f}")
        else:
            values.append("-")

    table = ax_tab.table(
        cellText=[values], 
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
def plotSA(results, save_path=None, show=True, title="Algorithm"):
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), gridspec_kw={"height_ratios": [3, 1]})
    ax_cost, ax_prob = axes[0]
    fig.delaxes(axes[1, 0])
    fig.delaxes(axes[1, 1])
    ax_tab = fig.add_subplot(2, 1, 2)

    for i, r in enumerate(results):
        cost_history = r.get("costHistory", [])
        if cost_history:
            ax_cost.plot(range(len(cost_history)), cost_history, linewidth=1.2, label=f"Run {i + 1}")

        prob_history = r.get("probabilityHistory", [])
        if prob_history:
            xs = [p[0] for p in prob_history]
            ys = [p[1] for p in prob_history]
            ax_prob.plot(xs, ys, linewidth=1, alpha=0.7, label=f"Run {i + 1}")

    ax_cost.set_title("Cost terhadap iterasi")
    ax_cost.set_xlabel("Iterasi")
    ax_cost.set_ylabel("Cost")
    ax_cost.grid(alpha=0.3)

    if results: ax_cost.legend()

    ax_prob.set_title("e^(ΔE/T) terhadap iterasi")
    ax_prob.set_xlabel("Iterasi")
    ax_prob.set_ylabel("e^(ΔE/T)")
    ax_prob.set_ylim(-0.02, 1.02)
    ax_prob.grid(alpha=0.3)

    ax_tab.axis("off")
    rows = []
    for i, r in enumerate(results):
        rows.append([
            r.get("finalVal", "-"),
            r.get("finalCost", "-"),
            f"{r.get('duration', 0):.1f}",
            r.get("iterations", len(r.get("costHistory", [])) - 1),
            r.get("rejectedWorseMoves", "-"),
        ])

    table = ax_tab.table(
        cellText=rows,
        colLabels=["Value", "Cost", "Durasi (s)", "Iterasi", "Stuck (Frekuensi move lebih buruk ditolak)"],
        loc="center",
        cellLoc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.auto_set_column_width(list(range(5)))
    table.scale(1, 1.8)
    ax_tab.axis("off")

    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.subplots_adjust(top=0.9, bottom=0.08, hspace=0.35, wspace=0.25)
    finish(fig, save_path, show)

def plotGA(results, save_path=None, show=True, title="Algorithm"):
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
            label=f"Best Cost"
        )

        # Biaya rata-rata seluruh populasi
        ax.plot(
            range(len(avg_history)),
            avg_history,
            linestyle="--",
            alpha=0.55,
            label=f"Average Cost"
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

