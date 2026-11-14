
"""
Generate the graph of the particle's path from the saved results.
"""
#------------------------------------------------------------------------------------------
# Imports and exceptions
#------------------------------------------------------------------------------------------

import json
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ModuleNotFoundError:
    print("Required libraries are not installed (matplotlib, numpy).")
    print("To install them, run the following in your terminal:")
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
# Plot
#------------------------------------------------------------------------------------------

def displacement_plot() -> bool:
    """
    Draw the saved path and write it to img/particle_path.png.

    Returns False (with an explanatory message) if the JSON does not exist,
    True when the image has been generated.
    """
    path = DATA_FOLDER / "walking_results.json"
    if not path.exists():
        print(f"  {path} was not found. Run this first:")
        print("    python3 random_walk.py --steps 10000 --seed 42 --save")
        return False

    # The path is a list ordered by step: [{x, y}, {x, y}, ...]
    data = json.loads(path.read_text(encoding="utf-8"))
    coordinates = data["path"]

    x = np.array([m["x"] for m in coordinates])
    y = np.array([m["y"] for m in coordinates])

    fig, ax = plt.subplots(figsize=(10, 10))

    # Thin, semi-transparent line: with 10,000 points a solid line would be a blob.
    ax.plot(x, y, linestyle="-", color="crimson",
            linewidth=0.5, alpha=0.6, label="Path", zorder=2)

    # Start (the origin) and end of the walk.
    ax.scatter(x[0], y[0], color="green", s=45, zorder=3, label="Start")
    ax.scatter(x[-1], y[-1], color="blue", s=45, zorder=3, label="End")

    ax.set_title(f"Random walk — {data['steps']:,} steps (seed {data['seed']})")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Layer order: grid at the bottom, black axes above it, path on top.
    ax.grid(alpha=0.3, which="both", zorder=0)
    ax.axhline(0, color="black", linewidth=1.1, zorder=1)
    ax.axvline(0, color="black", linewidth=1.1, zorder=1)
    # Equal scale and symmetric limits: the origin stays exactly at the center.
    ax.set_aspect("equal", adjustable="box")
    limit = max(np.abs(x).max(), np.abs(y).max()) * 1.05
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)

    ax.legend()
    fig.tight_layout()

    # 150 dpi x 10 in = 1500 x 1500 px.
    destination = IMG_FOLDER / "particle_path.png"
    fig.savefig(destination, dpi=150)
    plt.close(fig)
    print(f"  The plot was saved in '{destination}'")
    return True


#------------------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------------------

def main() -> int:
    """
    Create img/ if necessary, generate the graph, and return the exit code.
    """
    IMG_FOLDER.mkdir(exist_ok=True)

    ok = displacement_plot()
    if ok:
        print("\n  The plot is located in 'img/' and is version-controlled for the README.")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
