import math
from typing import Literal

_lookup_suffix_from_exp: dict[int, dict[str, str | float]] = {
    24: {"long": "yotta", "short": "Y", "scalar": 10**24},
    21: {"long": "zetta", "short": "Z", "scalar": 10**21},
    18: {"long": "exa", "short": "E", "scalar": 10**18},
    15: {"long": "peta", "short": "P", "scalar": 10**15},
    12: {"long": "tera", "short": "T", "scalar": 10**12},
    9: {"long": "giga", "short": "G", "scalar": 10**9},
    6: {"long": "mega", "short": "M", "scalar": 10**6},
    3: {"long": "kilo", "short": "k", "scalar": 10**3},
    0: {"long": "", "short": "", "scalar": 10**0},
    -3: {"long": "milli", "short": "m", "scalar": 10**-3},
    -6: {"long": "micro", "short": "µ", "scalar": 10**-6},
    -9: {"long": "nano", "short": "n", "scalar": 10**-9},
    -12: {"long": "pico", "short": "p", "scalar": 10**-12},
    -15: {"long": "femto", "short": "f", "scalar": 10**-15},
    -18: {"long": "atto", "short": "a", "scalar": 10**-18},
    -21: {"long": "zepto", "short": "z", "scalar": 10**-21},
    -24: {"long": "yocto", "short": "y", "scalar": 10**-24},
}


def si_format_value(
    value: float,
    unit: str,
    suffix_type: Literal["short", "long"] = "short",
    points_after_decimal: int = 2,
) -> str:
    """Format a value with SI suffix.

    Parameters
    ----------
    value: float
        The value to be formatted.

    unit: str
        The unit for the value. e.g. 'Hz'. For no unit use a blank string, ''.

    KwArgs
    ------
    suffix_type: str = "short"
        Default is short, options are 'short' or 'long'. e.g.
        'short' -> 1.0e9 Hz = 1.0 GHz.
        'long' -> 1.0e9 Hz = 1.0 GigaHz.

    points_after_decimal: int = 2
        Number of points to display after the decimal point. Default 2.
    """

    allowed_suffix_types = ["short", "long"]
    if suffix_type not in allowed_suffix_types:
        print(f"incorrect suffix_type, allowed values: {allowed_suffix_types}")
        return f"{value} {unit}"

    exponent_of_value = int(math.floor(math.log10(abs(value)) / 3.0) * 3)
    suffix_dict = _lookup_suffix_from_exp.get(exponent_of_value, None)

    if suffix_dict is None:
        print("unable to correctly format")
        return f"{value} {unit}"

    suffix = suffix_dict.get(suffix_type, "")

    scaled_value = value / suffix_dict.get("scalar")

    string = f"{scaled_value:.{points_after_decimal}f} {suffix}{unit}"

    return string
