from typing import Literal

import numpy as np
from numpy.typing import NDArray

freq_unit_name_to_exponent = {
    "Hz": 0,
    "KHz": 3,
    "MHz": 6,
    "GHz": 9,
    "THz": 12,
    "PHz": 15,
}


def freq_unit_change[T](
    f: T,
    current_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"],
    new_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"],
) -> T:
    if current_unit == new_unit:
        return f

    current_unit_exp = freq_unit_name_to_exponent[current_unit]
    new_unit_exp = freq_unit_name_to_exponent[new_unit]
    diff_in_exp = current_unit_exp - new_unit_exp

    new_f = f * (10**diff_in_exp)

    return new_f


def volts_to_db(Sxx_volts: NDArray) -> NDArray:
    """Transforming power Sxx volts**2 into decibells."""
    return 20 * np.log10(Sxx_volts)
