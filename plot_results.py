
#------------------------------------------------------------------------------------------
# Imports and exceptions
#------------------------------------------------------------------------------------------

import json
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ModuleNotFoundError:
    print("Matplotlib is not installed.")
    print("To install it, run the following in your terminal:")
    print("    pip install -r requirements.txt")
    print("Or, if you are using a virtual environment, use:")
    print("    source .venv/bin/activate && pip install -r requirements.txt")
    raise SystemExit(1) from None


#------------------------------------------------------------------------------------------
# Paths
#------------------------------------------------------------------------------------------

DATA_FOLDER = Path("results")
IMG_FOLDER = Path("img")


#------------------------------------------------------------------------------------------
# Graphic
#------------------------------------------------------------------------------------------

def displacement_plot() -> bool:
    path = DATA_FOLDER / "walking_results.json"
    if not path.exists():
        print(f"{path} was not found. Run this first:")
        print("    python3 random_walk.py --save")
        return False

    data = json.loads(path.read_text(encoding="utf-8"))
    coordinates = data["path"]

    x = np.array([m["x"] for m in coordinates])
    y = np.array([m["y"] for m in coordinates])

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.plot(x, y, linestyle="-", color="crimson",
            label="Movements", zorder=2)

    ax.set_title(f"Random walk — {data['steps']:,} steps (seed {data['seed']})")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    ax.grid(alpha=0.3, which="both", zorder=0)
    ax.axhline(0, color="black", linewidth=1.1, zorder=1)
    ax.axvline(0, color="black", linewidth=1.1, zorder=1)
    ax.set_aspect("equal", adjustable="box")
    limit = max(np.abs(x).max(), np.abs(y).max()) * 1.05
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)

    ax.legend()
    fig.tight_layout()

    destination = IMG_FOLDER / "particle_path.png"
    fig.savefig(destination, dpi=150)
    plt.close(fig)
    print(f"  The graphic was saved in '{destination}'")
    return True


#------------------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------------------

def main() -> int:
    IMG_FOLDER.mkdir(exist_ok=True)

    ok = displacement_plot()
    if ok:
        print("\n  The charts are located in 'img/' and are version-controlled for the README.")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
