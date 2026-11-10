
import argparse
import json
import sys
from pathlib import Path 
import numpy as np


#------------------------------------------------------------------------------------------
# Exceptions
#------------------------------------------------------------------------------------------

def positive_integer(text: str) -> int:
    try:
        """
        Exception for a non-integer value or string.
        """
        value = int(text)
    except ValueError as ve:
        raise argparse.ArgumentTypeError(f"`{text}` is not an integer. {ve}") from None

    if value <= 0:
        """
        Exception for a negative integer.
        """
        raise argparse.ArgumentTypeError("The number of steps must be positive.")

    return value


#------------------------------------------------------------------------------------------
# Data entry
#------------------------------------------------------------------------------------------
DEFAULT_STEPS = 10_000
DEFAULT_SEEDS = 100

def ask_integer(text: str, default: int, info: str) -> int:
    print(info)
    while True:
        answer = input(text).strip()
        if not answer:
            return default
        try:
            return positive_integer(answer)
        except argparse.ArgumentTypeError as exc:
            print(f"    {exc}. Try again.")

def ask_seed(text: str, default: int, info: str) -> int:
    print(info)
    while True:
        answer = input(text).strip()
        if not answer:
            return default
        try:
            return positive_integer(answer)
        except ValueError:
            print("     It is not an integer. Try again.")

def ask_yes_no(text: str, info: str) -> bool:
    print(info)
    answer = input(text).strip().lower()
    if answer in ("Y", "y", "Yes", "yes"):
        return True
    if answer in ("", "N", "n", "No", "no"):
        return False
    print("     Writes 'y' or 'n'.")

def fill_missing(args: argparse.Namespace) -> argparse.Namespace:
    missing = [
        args.steps is None,
        args.seed is None,
        args.save is None
    ]
    if not any(missing):
        return args

    if not sys.stdin.isatty():
        args.steps = args.steps or DEFAULT_STEPS
        args.seed = args.seed or DEFAULT_SEEDS
        args.save = bool(args.save)
        return args

    print("\n  Values ​​not defined in the terminal.")
    print("\n  Press Enter to accept the default value.\n")

    if args.steps is None:
        args.steps = ask_integer(
            "Number of steps.",
            DEFAULT_STEPS,
            info=(
                "  Number of displacements (steps) that the "
                "    particle will make in the Cartesian plane."
            )
        )

    if args.seed is None:
        args.seed = ask_seed(
            "Number of seeds",
            DEFAULT_SEEDS,
            info=(
                "  Random number generator seed.\n" 
                "    A specific number determines the outcome: the results\n" 
                "    are always the same, allowing the experiment to be repeated.\n" 
                "    Enter = a different outcome each time."
            )
        )

    if args.save is None:
        args.save = ask_yes_no(
            "   Save JSON results?   [n]:",
            info=(
                "  Save the results?\n" 
                "    Write the numbers to files in the 'results/' directory. Then,\n" 
                "    'plot_results.py' plots the simulation of the particle's displacement."
            )
        )

    return args


#------------------------------------------------------------------------------------------
# Walking calculation
#------------------------------------------------------------------------------------------

def random_walks(steps: int, rng: np.random.Generator) -> dict[dict]:

    position = {
        "x": 0,
        "y": 0
    }

    displacements = [
        {"Dx": 0, "Dy": 1},
        {"Dx": 0, "Dy": -1},
        {"Dx": 1, "Dy": 0},
        {"Dx": -1, "Dy": 0},
    ]
    Dposition = rng.choices(displacements, k=steps)

    step_dict = {
        0: {"x": 0, "y": 0}
    }
    for i in Dposition:

        position = {
            "x": position["x"] + Dposition[i]["Dx"],
            "y": position["y"] + Dposition[i]["Dy"]
        }
        step_dict[i + 1] = position

    return step_dict


#------------------------------------------------------------------------------------------
# Presentation
#------------------------------------------------------------------------------------------

# def print_result():
#     print("\n")

#------------------------------------------------------------------------------------------
# Persistence - En esta seccion se agrega la funcion para guardar en JSON
#------------------------------------------------------------------------------------------

def save_json(route: Path, data: dict) -> None:
    route.parent.mkdir(parents=True, exist_ok=True)
    route.write_text(json.dump(data, indent=2), encoding="utf-8")
    print(f"  The results were saved in the {route} directory.")


#------------------------------------------------------------------------------------------
# Command-line interface
#------------------------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="random_walk.py",
        description="Simulation of the random displacement of a particle",
        epilog=(
            "Examples:\n"
            "  python3 random_walk.py\n"
            "  python3 random_walk.py --n 100\n"
            "  python3 random_walk.py --seed 43\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--steps",
        type=positive_integer,
        metavar="Stp",
        default=None,
        help=(
            "Number of unit steps in which the particle will move."
            "Four basic movements are defined: up, down, left and right."
            "If it is not written, it is asked (def. 1000)."
        )
    )

    parser.add_argument(
        "--seed",
        type=int,
        metavar="S",
        default=None,
        help="Random generator seed, for reproducible results."
    )

    parser.add_argument(
        "-s", "-save",
        action="store_true",
        default=None,
        help="Save the results in the 'results/' folder."
    )

    parser.add_argument(
        "-force",
        action="store_true",
        help="Allow --convergence even if the memory limit is exceeded."
    )

    return parser

# BYTES_PER_POINT = 32
# MEMORY_LIMIT_GB = 1.5
# Falta agregar el main y dentro se invoca la funcion para guardar en JSON

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args = fill_missing(args)

    rng = np.random.default_rng(args.seed)

    print("\n  Simulation of the random displacement of a particle.")
    print(f"  Seed: {args.seed if args.seed is not None else 'random'}")

    hike = random_walks(args.steps, rng)

    if args.save:
        save_json(
            Path("results") / "walking_results.json",
            {
                "number of steps": args.steps,
                "seed": args.seed,
                "path": [hike]
            }
        )

        return 0

    if __name__ == "__main__":
        raise SystemExit(main())
