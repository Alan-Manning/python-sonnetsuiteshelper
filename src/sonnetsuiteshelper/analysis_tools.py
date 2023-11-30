import os

import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.optimize import curve_fit
from scipy.signal import find_peaks


def S21_mag_fit(freqs, f0, qr, qc):
    """
    Fit for the S21 mag against frequency
    """
    xr = freqs / f0 - 1
    s21 = 1 - ((qr / qc) * (1 / (1 + 2j * qr * xr)))
    return np.abs(s21)


def volts_to_db(S21_volts):
    """
    Transforming power S21 volts**2 into decibells
    """
    return 20 * np.log10(S21_volts)


class SonnetCSVOutputFile:
    """
    csv output object.

    Loads in a csv output generated from a sonnet and provides functions to
    analyse that data.

    Parameters
    ----------
    file_name : str
        The name of the file.

    file_path : str
        The path of the file.

    Parameter : str
        The parameter type of the csv output file from sonnet. Default is "S-Param".

    complex : str
        the complex type of the csv output file from sonnet. Default is "Real-Imag".

    """

    def __init__(self, file_name: str, file_path: str = "", parameter: str = "S-Param", complex: str = "Real-Imag"):
        # if no .csv file extention it is added.
        if file_name[-4:] != ".csv":
            file_name = file_name + ".csv"

        live_file = os.path.join(file_path, file_name)

        file_exists = os.path.isfile(live_file)
        if not file_exists:
            raise (FileNotFoundError)

        # read csv

        csv_col_names = ["Frequency (GHz)", "RE[S11]", "IM[S11]", "RE[S12]", "IM[S12]", "RE[S21]", "IM[S21]", "RE[S22]", "IM[S22]"]

        # itterate to find start of the file's data
        skip_row = 2
        start_is_NaN = True

        while start_is_NaN:
            file_data = pd.read_csv(live_file, names=csv_col_names, skiprows=skip_row)
            if isinstance(file_data["Frequency (GHz)"][0], str):
                skip_row += 1
            else:
                start_is_NaN = False

        self.file_data = file_data
        self.freqs = np.array(self.file_data["Frequency (GHz)"] * 1e9)  # converty GHz to Hz
        self.S21_mag = np.abs(file_data["RE[S21]"] + 1j * file_data["IM[S21]"])

    def __str__(self):
        return f"SonnetCSVOutputFile\n\tname: {self.file_name}\n\tParameter: {self.parameter}\n\tComplex: {self.complex}"

    def get_resonant_freq(self) -> float:
        """
        Get the resonant frequency (*in Hz*) from the data
        """
        # find the peak in the data
        peaks_in_data = find_peaks(self.S21_mag, height=5, distance=100)
        try:
            peak_index = peaks_in_data[0][0]
        except IndexError as no_peak:
            print(no_peak)

        no_points_around_peak = 200

        # Get the freqs and S21_mag around the peak
        freqs_around_peak = np.array(self.freqs[(peak_index - no_points_around_peak) : (peak_index + no_points_around_peak)])
        S21_mag_around_peak = np.array(self.S21_mag[(peak_index - no_points_around_peak) : (peak_index + no_points_around_peak)])

        # take the freq at the lowest point in the peak
        resonant_freq = freqs_around_peak[S21_mag_around_peak.argmin()]
        return resonant_freq

    def get_Q_values(self):
        """
        Get the Q values from the data
        Returns a list containing the QR, QC and QI values
        """

        # find the peak in the data
        peaks_in_data = find_peaks(self.S21_mag, height=5, distance=100)
        try:
            peak_index = peaks_in_data[0][0]
        except IndexError as no_peak:
            print(no_peak)

        no_points_around_peak = 200

        # Get the freqs and S21_mag around the peak
        freqs_around_peak = np.array(self.freqs[(peak_index - no_points_around_peak) : (peak_index + no_points_around_peak)])
        S21_mag_around_peak = np.array(self.S21_mag[(peak_index - no_points_around_peak) : (peak_index + no_points_around_peak)])

        init_QR_guess = 10e3
        init_QC_guess = 2 * init_QR_guess
        init_guesses = np.array([self.resonant_freq(), init_QR_guess, init_QC_guess])
        popt, pcov = curve_fit(S21_mag_fit, freqs_around_peak, S21_mag_around_peak, p0=init_guesses)
        QR = popt[1]
        QC = popt[2]
        QI = 1 / ((1 / QR) - (1 / QC))

        return [QR, QC, QI]

    def get_three_dB_BW(self):
        """
        get the 3dB BW from the peak in the data
        """
        spline = UnivariateSpline(self.freqs, volts_to_db(self.S21_mag) + 3.0, s=0)
        return abs(spline.roots()[1] - spline.roots()[0])
