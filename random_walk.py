
"""
Simulation of a particle's random walk in the plane.

The particle starts at the origin and takes unit steps in one of the four
cardinal directions. The result can be saved as JSON and plotted with
plot_results.py.
"""
import argparse
import json
import sys
from pathlib import Path
import numpy as np


#------------------------------------------------------------------------------------------
# Exceptions
#------------------------------------------------------------------------------------------

def positive_integer(text: str) -> int:
    """
    EXCEPTION

    Convert the text to an integer and verify that it is greater than zero.

    argparse catches the exception and displays a clean message, instead of
    letting the program crash with a traceback.
    """
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
    """
    EXCEPTION

    Convert the text to an integer and verify that it is not negative.
    Used for the seed, which must be 0 or higher.
    """
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
# Default number of steps when --steps is not given.
DEFAULT_STEPS = 10_000

def ask_integer(prompt: str, default: int, info: str) -> int:
    """Ask until a positive integer is typed; Enter accepts the default."""
    print(info)
    while True:
        answer = input(prompt).strip()
        if not answer:
            return default
        try:
            return positive_integer(answer)
        except argparse.ArgumentTypeError as exc:
            print(f"{exc} Try again.")


def ask_seed(prompt: str, info: str) -> int | None:
    """Ask for a seed; Enter returns None so a random one is generated."""
    print(info)
    while True:
        answer = input(prompt).strip()
        if not answer:
            return None
        try:
            return non_negative_integer(answer)
        except argparse.ArgumentTypeError as exc:
            print(f"{exc} Try again.")


def ask_yes_no(prompt: str, info: str) -> bool:
    """Ask a yes/no question; Enter (empty) and 'n' mean no."""
    print(info)
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("", "n", "no"):
            return False
        print("Type 'y' or 'n'.")


def fill_missing(args: argparse.Namespace) -> argparse.Namespace:
    """
    Prompt for any argument that was not given on the command line.

    If stdin is not a terminal (pipe or script), nothing is asked and the
    defaults are applied, so the program never hangs waiting for input.
    """
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

    print("\n  Some values were not given on the command line.")
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
                "  Press Enter to use a random seed each time."
            )
        )

    if args.save is None:
        args.save = ask_yes_no(
            "Save JSON results? [y/N]:",
            info=(
                "  The walk will be saved as JSON in the 'results/' folder.\n"
                "  Then 'plot_results.py' plots the path of the particle."
            )
        )

    return args


#------------------------------------------------------------------------------------------
# Walking calculation
#------------------------------------------------------------------------------------------

def random_walk(steps: int, rng: np.random.Generator) -> list[dict[str, int]]:
    """
    Take `steps` unit steps in one of four directions and return the path.

    The result is a list of {"x", "y"} positions where the index IS the
    step number: element 0 is the origin, element k is the position after
    step k (so the list has steps + 1 entries).
    """
    position = {
        "x": 0,
        "y": 0
    }

    # The four basic movements: up, down, left and right.
    displacements = [
        {"dx": 0, "dy": 1},
        {"dx": 0, "dy": -1},
        {"dx": 1, "dy": 0},
        {"dx": -1, "dy": 0},
    ]
    # All displacements are drawn at once (vectorized).
    deltas = rng.choice(displacements, size=steps)

    # Index 0 of the list is the origin (step 0).
    step_list = [position.copy()]
    for delta in deltas:

        position = {
            "x": position["x"] + delta["dx"],
            "y": position["y"] + delta["dy"]
        }
        step_list.append(position)

    return step_list


#------------------------------------------------------------------------------------------
# Persistence
#------------------------------------------------------------------------------------------

def save_json(file: Path, data: dict) -> None:
    """
    Create the folder if necessary and write `data` as indented JSON.
    """
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  The results were saved in '{file}'")


#------------------------------------------------------------------------------------------
# Command-line interface
#------------------------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """
    Define the command-line interface (all options are optional).
    """
    parser = argparse.ArgumentParser(
        prog="random_walk.py",
        description="Simulation of a particle's random walk",
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
        metavar="STEPS",
        default=None,
        help=(
            "Number of unit steps in which the particle will move.\n"
            "Four basic movements are defined: up, down, left and right.\n"
            "If omitted, you will be asked (default: 10000)."
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
#   1 position dict ({"x", "y"} ≈ 184 B) + its entry in the step list
#   + the reference in the displacement array ≈ 230 bytes
#   (measured with tracemalloc: 221 B at 200,000 steps, 231 B at 500,000;
#   rounded up to leave a margin)
BYTES_PER_STEP = 250
# Safety ceiling of 1.5 GB of RAM, the same as montecarlo_pi.py.
MEMORY_LIMIT_GB = 1.5

def main(argv: list[str] | None = None) -> int:
    """
    Entry point: parse the arguments, simulate, and return the exit code
    (0 on success, 1 if the memory limit is exceeded).
    """
    args = build_parser().parse_args(argv)

    # First, the values are filled in, because the subsequent memory
    # check needs to know how many steps will be used.
    args = fill_missing(args)

    memory_gb = args.steps * BYTES_PER_STEP / 1e9
    if memory_gb > MEMORY_LIMIT_GB and not args.force:
        maximum = int(MEMORY_LIMIT_GB * 1e9 / BYTES_PER_STEP)
        print(file=sys.stderr)
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

    # Generate a seed when none was given, and print it, so the
    # experiment can be reproduced later with the same number.
    if args.seed is None:
        args.seed = int(np.random.SeedSequence().generate_state(1)[0])

    rng = np.random.default_rng(args.seed)

    print("  Simulation of a particle's random walk.")
    print(f"  Seed: {args.seed}")

    walk = random_walk(args.steps, rng)

    if args.save:
        save_json(
            Path("results") / "walking_results.json",
            {
                "steps": args.steps,
                "seed": args.seed,
                "path": walk
            }
        )
        print("  To generate the plot, run:")
        print("    python3 plot_results.py\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
