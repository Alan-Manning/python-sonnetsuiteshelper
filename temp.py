from collections.abc import Sequence
from typing import Literal

from numpy import pi


def bend_diff_frac(bend_rad: float):
    normal_len = 2
    len_of_bend = pi * bend_rad * 0.5

    return len_of_bend / normal_len


def get_len_of_90_deg_bend(bend_rad: float) -> float:
    """Get the len of a 90 deg round bend."""
    return pi * bend_rad * 0.5


def get_total_len(lens: list[float], bend_rad: float) -> float:
    """Get the total length of feedline with 90 deg bends after each len given
    but not before or after the first and last respectively. feedline lens
    should be given from the center of the feedline.

    Parameters
    ----------
    lens: list[float]
        the list of lens.

    bend_rad: float
        the bend radius of the corners.

    Returns
    -------
    total_len: float
        The total length accounting for corners
    """
    bend_len = get_len_of_90_deg_bend(bend_rad)
    ###########################################################################

    total_len: float = 0.0
    relative_lens: list[float] = []

    len_up_to_bend = lens[0] - bend_rad

    total_len += len_up_to_bend
    total_len += bend_len

    for len in lens[1::-1]:
        len_minus_prev_bend = len - bend_rad
        len_up_to_next_bend = len_minus_prev_bend - bend_rad

        total_len += len_up_to_next_bend
        total_len += bend_len

    len_minus_prev_bend = lens[-1] - bend_rad
    total_len += len_minus_prev_bend

    return total_len


def get_relative_lens(lens: Sequence[float | Literal["bend", "res"]], bend_rad: float) -> tuple[list[float], float]:
    """Get the relative length of resonators on a feedline with 90 deg bends.
    feedline lens should be given from the center of the feedline.

    Parameters
    ----------
    lens: Sequence[float | Literal["bend", "rad"]]
        the list of lens or the directive for bend or res. give a len up to
        either a bend or a rad or just a len.

    bend_rad: float
        the bend radius of the corners.

    Returns
    -------
    ( rel_res_lens, total_len ): tuple[list[float], float]
        The relative len each resonator sits in the feedline and the total
        length of that feedline.
    """

    bend_len = get_len_of_90_deg_bend(bend_rad)

    running_len: float = 0
    rel_res_lens: list[float] = []

    for len in lens:
        if isinstance(len, float | int):
            running_len += len
        else:
            if len == "bend":
                running_len - bend_rad
                running_len += bend_len
                running_len - bend_rad
            if len == "res":
                rel_res_lens.append(running_len)
        # print()
        # print(f"{len=}")
        # print(f"{running_len=}")
        # print(f"{rel_res_lens=}")

    return rel_res_lens, running_len


def main() -> None:
    LW: float = 36.0
    bend_rad = 200.0

    lens: list[float | str] = [
        3834.5 + (LW / 2),
        "bend",
        9150.91,
        "bend",
        # top left vert
        1352.5,
        "bend",
        # top row res
        526.91 + 1.5 + (LW / 2),
        "res",
        5209,
        "res",
        6791,
        "res",
        5209,
        "res",
        526.91 + 1.5 + (LW / 2),
        "bend",
        #
        4590,
        "bend",
        # 2nd row res
        526.91 + 1.5 + (LW / 2),
        "res",
        5209,
        "res",
        6791,
        "res",
        5209,
        "res",
        526.91 + 1.5 + (LW / 2),
        "bend",
        # mid left vert
        7410,
        "bend",
        # 3rd row res
        526.91 + 1.5 + (LW / 2),
        "res",
        5209,
        "res",
        6791,
        "res",
        5209,
        "res",
        526.91 + 1.5 + (LW / 2),
        "bend",
        #
        4590,
        "bend",
        # 4th row res
        526.91 + 1.5 + (LW / 2),
        "res",
        5209,
        "res",
        6791,
        "res",
        5209,
        "res",
        526.91 + 1.5 + (LW / 2),
        "bend",
        1352.5,
        "bend",
        # bot left vert
        9150.91,
        "bend",
        3834.5 + (LW / 2),
    ]

    # total_len = get_total_len(lens, bend_rad)
    # print(total_len)
    rel_res_lens, total_len = get_relative_lens(lens, bend_rad)
    print(f"total len: {total_len}")

    ids = (
        0,
        4,
        1,
        5,
        #
        13,
        9,
        12,
        8,
        #
        2,
        6,
        3,
        7,
        #
        15,
        11,
        14,
        10,
    )
    for id, len in zip(ids, rel_res_lens, strict=True):
        print(f"ID:{id} - RelLen:{len:.2f}")


if __name__ == "__main__":
    main()
