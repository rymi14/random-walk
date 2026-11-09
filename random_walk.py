
import argparse
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
# Walking calculation
#------------------------------------------------------------------------------------------

def random_walks(n: int):



    position = {
        "x": 0,
        "y": 0
    }
    print(f"P_0 = {position}")

    displacements = [
        {"Dx": 0, "Dy": 1},
        {"Dx": 0, "Dy": -1},
        {"Dx": 1, "Dy": 0},
        {"Dx": -1, "Dy": 0},
    ]

    Dposition = np.random.choice(displacements)
    print(f"∆P = {Dposition}")

    position = {
        "x": position["x"] + Dposition["Dx"],
        "y": position["y"] + Dposition["Dy"]
    }

    return print(f"Nueva posicion \nP_1 = {position}")


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

    return parser
