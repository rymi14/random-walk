
import argparse
import json
import sys
from pathlib import Path
import numpy as np


#------------------------------------------------------------------------------------------
# Exceptions
#------------------------------------------------------------------------------------------

def positive_integer(text: str) -> int:
    # Exception for a non-integer value or string.
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"`{text}` is not an integer.") from None
    # Exception for a non-positive integer.
    if value <= 0:
        raise argparse.ArgumentTypeError("The number of steps must be positive.")

    return value


def non_negative_integer(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"`{text}` is not an integer.") from None
    if value < 0:
        raise argparse.ArgumentTypeError("The seed must be 0 or higher.")
    return value


#------------------------------------------------------------------------------------------
# Data entry
#------------------------------------------------------------------------------------------
DEFAULT_STEPS = 10_000

def ask_integer(text: str, default: int, info: str) -> int:
    print(info)
    while True:
        answer = input(text).strip()
        if not answer:
            return default
        try:
            return positive_integer(answer)
        except argparse.ArgumentTypeError as exc:
            print(f"    {exc} Try again.")


def ask_seed(text: str, info: str) -> int | None:
    print(info)
    while True:
        answer = input(text).strip()
        if not answer:
            return None
        try:
            return non_negative_integer(answer)
        except argparse.ArgumentTypeError as exc:
            print(f"     {exc} Try again.")


def ask_yes_no(text: str, info: str) -> bool:
    print(info)
    while True:
        answer = input(text).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("", "n", "no"):
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
        args.save = bool(args.save)
        return args

    print("\n  Values not defined in the terminal.")
    print("\n  Press Enter to accept the default value.\n")

    if args.steps is None:
        args.steps = ask_integer(
            "Number of steps:",
            DEFAULT_STEPS,
            info=(
                "  Number of displacements (steps) that the\n"
                "  particle will make in the Cartesian plane."
            )
        )

    if args.seed is None:
        args.seed = ask_seed(
            "Seed [Enter = random]:",
            info=(
                "  Random number generator seed.\n"
                "  A specific number determines the outcome: the results\n"
                "  are always the same, allowing the experiment to be repeated.\n"
                "  Enter = a different outcome each time."
            )
        )

    if args.save is None:
        args.save = ask_yes_no(
            "   Save JSON results?   [n]:",
            info=(
                "  Save the results?\n"
                "  Write the numbers to files in the 'results/' directory. Then,\n"
                "  'plot_results.py' plots the simulation of the particle's displacement."
            )
        )

    return args


#------------------------------------------------------------------------------------------
# Walking calculation
#------------------------------------------------------------------------------------------

def random_walks(steps: int, rng: np.random.Generator) -> dict[str, dict[str, int]]:

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
    Dposition = rng.choice(displacements, size=steps)

    digits = len(str(steps))

    step_dict = {
        f"{0:0{digits}d}": {"x": 0, "y": 0}
    }
    for i, delta in enumerate(Dposition, start=1):

        position = {
            "x": position["x"] + delta["Dx"],
            "y": position["y"] + delta["Dy"]
        }
        step_dict[f"{i:0{digits}d}"] = position

    return step_dict


#------------------------------------------------------------------------------------------
# Persistence
#------------------------------------------------------------------------------------------

def save_json(route: Path, data: dict) -> None:
    route.parent.mkdir(parents=True, exist_ok=True)
    with route.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  The results were saved in {route}.")


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
            "  python3 random_walk.py --steps 10000\n"
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
            "Number of unit steps in which the particle will move.\n"
            "Four basic movements are defined: up, down, left and right.\n"
            "If it is not written, it is asked (def. 10000)."
        )
    )

    parser.add_argument(
        "--seed",
        type=non_negative_integer,
        metavar="S",
        default=None,
        help=(
            "Random generator seed (non-negative), for\n"
            "reproducible results."
        )
    )

    parser.add_argument(
        "-s", "--save",
        action="store_true",
        default=None,
        help="Save the results in the 'results/' folder."
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Run the simulation even if the estimated memory exceeds the limit."
    )

    return parser


# Approximate memory required per step of the walk:
#   1 position dict ({"x", "y"} = 184 B) + 1 zero-padded key (47 B)
#   + its entry in step_dict + the reference in the displacement array ≈ 300 bytes
BYTES_PER_STEP = 300
MEMORY_LIMIT_GB = 1.5

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # First, the values are filled in, because the subsequent memory
    # check needs to know how many steps will be used.
    args = fill_missing(args)

    memory_gb = args.steps * BYTES_PER_STEP / 1e9
    if memory_gb > MEMORY_LIMIT_GB and not args.force:
        maximum = int(MEMORY_LIMIT_GB * 1e9 / BYTES_PER_STEP)
        print()
        print(
            f"  --steps {args.steps:,} requires "
            f"{memory_gb:.1f} GB of memory,\n"
            f"and the safety limit is {MEMORY_LIMIT_GB} GB.",
            file=sys.stderr
        )
        print(
            f"  Use --steps {maximum:,} or less, or add --force\n"
            f"  if you really want to try.",
            file=sys.stderr
        )
        return 1

    if args.seed is None:
        args.seed = int(np.random.SeedSequence().generate_state(1)[0])

    rng = np.random.default_rng(args.seed)

    print("\n  Simulation of the random displacement of a particle.")
    print(f"  Seed: {args.seed}")

    hike = random_walks(args.steps, rng)

    if args.save:
        save_json(
            Path("results") / "walking_results.json",
            {
                "number of steps": args.steps,
                "seed": args.seed,
                "path": hike
            }
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
