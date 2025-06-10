from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import UnivariateSpline
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

from .bases import SingleResonatorAnalyser
from .output_files.base_param import SParamOutput
from .utils.fitting import S21_mag_fit


class QValues(NamedTuple):
    QR: float
    QC: float
    QI: float


class SParamSingleResonatorAnalyser(SingleResonatorAnalyser):
    """SParamSingleResonator."""

    def __init__(
        self,
        s_param_output: SParamOutput,
    ) -> None:
        self.s_param_output = s_param_output
        return

    def get_resonant_freq(self) -> float:
        """Get the resonant frequency (Hz) from the data.

        Returns
        -------
        resonant_freq : float
            The resonant frequency in Hz of the peak in the data.
        """
        S21_mag_dB = self.s_param_output.Sxx_mag_dB(2, 1)

        resonant_freq = float(self.s_param_output.get_freqs()[S21_mag_dB.argmin()])

        return resonant_freq

    def get_Q_values(self) -> QValues:
        """Get the Q values from the data around the peak. Returns QR, QC, QI.

        Returns
        -------
        Q_vals : QValues
            tuple containing (QR, QC, QI).
        """

        freqs = self.s_param_output.get_freqs()
        S21_mag = self.s_param_output.Sxx_mag(2, 1)

        init_QR_guess = 10e3
        init_QC_guess = 2 * init_QR_guess
        init_guesses = np.array([self.get_resonant_freq(), init_QR_guess, init_QC_guess])
        popt, _ = curve_fit(S21_mag_fit, freqs, S21_mag, p0=init_guesses)
        QR = popt[1]
        QC = popt[2]
        QI = 1 / ((1 / QR) - (1 / QC))

        Q_vals = QValues(QR, QC, QI)

        return Q_vals

    def get_three_dB_BW(self) -> float:
        """Get the 3dB BW in Hz from the peak in the data."""
        freqs = self.s_param_output.get_freqs()
        S21_mag_dB = self.s_param_output.Sxx_mag_dB(2, 1)

        # shift the S21_mag_dB up by 3
        y_shifted_S21_mag_dB = S21_mag_dB + 3.0

        # convert to spline and take the points where it corsses the x-axis. This is the 3dB BW
        spline = UnivariateSpline(freqs, y_shifted_S21_mag_dB, s=0)
        roots = spline.roots()
        match len(roots):
            case 2:
                three_dB_BW = roots[1] - roots[0]
                return abs(three_dB_BW)
            case 0:
                msg = "Likely because of dip depth not being 3dB or more."
            case 1:
                msg = "Could only find one point where dip depth is 3dB or more."
            case _:
                msg = "Found multiple points where dip depth is 3dB or more. Possible multiple resonances or noisy output."

        raise RuntimeError(f"Could not find 3dB bandwidth in file: `{self.s_param_output.filename}`. {msg}")

    # def _get_indices_around_peak(
    #     self,
    #     y_data: NDArray,
    #     no_points_around_peak: int | None = None,
    # ) -> list[int]:
    #     """Get the indices around the peak in the data."""
    #
    #     if no_points_around_peak is None:
    #         no_points_around_peak = 300
    #
    #     if not isinstance(no_points_around_peak, int):
    #         raise TypeError(f"no_points_around_peak should be of type int, found type {type(no_points_around_peak)}.")
    #
    #     peaks_in_data, _ = find_peaks(y_data)
    #     if len(peaks_in_data) == 0:
    #         raise RuntimeError(f"No Peaks found in data for file: '{self.s_param_output.filename}'.")
    #
    #     peak_index = peaks_in_data[0][0]
    #
    #     # Get the range around the peak being sure to not overflow the original
    #     # array by indexing outside its length
    #     lower_range_index = max([peak_index - no_points_around_peak, 0])
    #     upper_range_index = min([peak_index + no_points_around_peak, len(y_data)])
    #
    #     indices_around_peak = list(range(lower_range_index, upper_range_index))
    #
    #     return indices_around_peak
