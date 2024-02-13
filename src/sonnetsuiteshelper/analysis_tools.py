import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.interpolate import UnivariateSpline
from scipy.optimize import curve_fit
from scipy.signal import find_peaks


def S21_mag_fit(freqs, f0, qr, qc):
    """Fit for the S21 mag against frequency."""
    xr = freqs / f0 - 1
    s21 = 1 - ((qr / qc) * (1 / (1 + 2j * qr * xr)))
    return np.abs(s21)


def volts_to_db(S21_volts):
    """Transforming power S21 volts**2 into decibells."""
    return 20 * np.log10(S21_volts)


class SonnetCSVOutputFile:
    """Csv output object.

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

        self.file_name = file_name[:-4]

        live_file = os.path.join(file_path, file_name)

        file_exists = os.path.isfile(live_file)
        if not file_exists:
            raise (FileNotFoundError)

        # read csv

        csv_col_names = ["Frequency (GHz)", "RE[S11]", "IM[S11]", "RE[S12]", "IM[S12]", "RE[S21]", "IM[S21]", "RE[S22]", "IM[S22]"]

        # itterate to find start of the file's data
        skip_row = 2
        file_data = pd.read_csv(live_file, names=csv_col_names, skiprows=skip_row)

        while isinstance(file_data["Frequency (GHz)"][0], str):
            file_data = pd.read_csv(live_file, names=csv_col_names, skiprows=skip_row)
            skip_row += 1

        self.file_data = file_data
        self.freqs = np.array(self.file_data["Frequency (GHz)"] * 1e9)  # converty GHz to Hz
        self.S21_mag = np.array(np.abs(file_data["RE[S21]"] + 1j * file_data["IM[S21]"]))
        self.S21_mag_dB = volts_to_db(self.S21_mag)

    def __str__(self):
        return f"SonnetCSVOutputFile\n\tname: {self.file_name}\n\tParameter: {self.parameter}\n\tComplex: {self.complex}"

    def _get_indices_around_peak(self, y_data: list, no_points_around_peak: int = 200) -> list:
        """Get the indices around the peak in the data."""
        peaks_in_data = find_peaks(y_data, height=5, distance=100)
        if len(peaks_in_data[0]) == 0:
            raise (Exception("No Peaks found in data"))

        peak_index = peaks_in_data[0][0]

        # Get the range around the peak being sure to not overflow the original
        # array by indexing outside its length
        lower_range_index = max([peak_index - no_points_around_peak, 0])
        upper_range_index = min([peak_index + no_points_around_peak, len(y_data)])

        indices_around_peak = range(lower_range_index, upper_range_index)
        indices_around_peak = range(peak_index - no_points_around_peak, peak_index + no_points_around_peak)

        return indices_around_peak

    def plot_data(
        self, x_ax: str = "freq_MHz", y_ax: str = "S21_mag_dB", data_points_around_peak: int = 0, fig_ax: plt.Axes = None
    ) -> None:
        """Plots the data in the csv, default is plotting all data in the
        S21_mag_dB against freq. This can take differing x_ax and y_ax values
        to plot. Can also just plot region around the peak in the data by
        passing a data_points_around_peak value.

        KwArgs
        ----------
        x_ax : str
            The data to plot on the x axis. Default is the frequency in units
            of MHz. This parameter can take any of the values,
            ["freq_Hz", "freq_MHz", "freq_GHz"].

        y_ax : str
            The data to plot on the y axis. Default is the S21 magnitude in
            units of decibells. This parameter can take any of the values,
            ["S21_mag", "S21_mag_dB"].

        data_points_around_peak : int
            The number of data points either side of the peak in the data to
            plot. By default this value is 0 which will plot all the data.

        fig_ax : plt.Axes
            This is a matplotlib axes which, when defined, will be the axes the
            data is plotted to. This allows for customizing the look and adding
            extra data to the plot.
        """

        x_lookup = {
            "freq_Hz": {"data": self.freqs, "label": "freq", "units": "Hz"},
            "freq_MHz": {"data": self.freqs * 1e-6, "label": "freq", "units": "MHz"},
            "freq_GHz": {"data": self.freqs * 1e-9, "label": "freq", "units": "GHz"},
        }

        y_lookup = {
            "S21_mag": {"data": self.S21_mag, "label": "S21 mag", "units": "V**2"},
            "S21_mag_dB": {"data": volts_to_db(self.S21_mag), "label": "S21 mag", "units": "dB"},
        }

        if x_ax not in x_lookup.keys():
            raise KeyError("{x_ax} is an invalid value for x_ax. Valid values are {list(x_lookup.keys())}")

        if y_ax not in y_lookup.keys():
            raise KeyError("{y_ax} is an invalid value for y_ax. Valid values are {list(y_lookup.keys())}")

        x_data = x_lookup[x_ax]["data"]
        x_label = x_lookup[x_ax]["label"]
        x_units = x_lookup[x_ax]["units"]

        y_data = y_lookup[y_ax]["data"]
        y_label = y_lookup[y_ax]["label"]
        y_units = y_lookup[y_ax]["units"]

        title = f"File = {self.file_name}"
        col = "C0"

        if data_points_around_peak != 0:
            region = self._get_indices_around_peak(-self.S21_mag_dB, no_points_around_peak=data_points_around_peak)
            y_data = y_lookup[y_ax]["data"][region]
            x_data = x_lookup[x_ax]["data"][region]
            title += f"   ({data_points_around_peak}_points_around_peak)"
            col = "C1"

        # If a matplotlib figure axes is defined just plot the data to that.
        if fig_ax:
            fig_ax.scatter(x_data, y_data, s=0.5, color=col)
            fig_ax.plot(x_data, y_data, linewidth=0.2, alpha=0.3, color=col)
            fig_ax.set_xlabel(f"{x_label}     ({x_units})")
            fig_ax.set_ylabel(f"{y_label}     ({y_units})")
            return

        fig = plt.figure(title)
        rows = 1
        cols = 1
        grid = plt.GridSpec(rows, cols)  # , top=0.95, bottom=0.092, left=0.05, right=0.95, hspace=0.0, wspace=0.2)

        ax0 = plt.subplot(grid[0, 0])

        ax0.scatter(x_data, y_data, s=0.5, color=col)
        ax0.plot(x_data, y_data, linewidth=0.2, alpha=0.3, color=col)

        ax0.set_title(title, loc="left")
        ax0.set_xlabel(f"{x_label}     ({x_units})")
        ax0.set_ylabel(f"{y_label}     ({y_units})")
        ax0.grid(alpha=0.3)

        fig.show()

    def get_resonant_freq(self) -> float:
        """Get the resonant frequency (*in Hz*) from the data.

        Returns
        -------
        resonant_freq : float
            The resonant frequency of the peak in the data.
        """
        # find the peak in the data
        indices_around_peak = self._get_indices_around_peak(-self.S21_mag_dB)

        # Get the freqs and S21_mag around the peak
        freqs_around_peak = self.freqs[indices_around_peak]
        S21_mag_dB_around_peak = self.S21_mag_dB[indices_around_peak]

        # take the freq at the lowest point in the peak
        resonant_freq = freqs_around_peak[S21_mag_dB_around_peak.argmin()]

        return resonant_freq

    def get_Q_values(self) -> list:
        """Get the Q values from the data. Returns a list containing the QR, QC
        and QI values.

        Returns
        -------
        Q_Values : list
            list containing [QR, QC, QI].
        """

        # find the peak in the data
        indices_around_peak = self._get_indices_around_peak(-self.S21_mag_dB)

        # Get the freqs and S21_mag around the peak
        freqs_around_peak = self.freqs[indices_around_peak]
        S21_mag_around_peak = self.S21_mag[indices_around_peak]

        init_QR_guess = 10e3
        init_QC_guess = 2 * init_QR_guess
        init_guesses = np.array([self.get_resonant_freq(), init_QR_guess, init_QC_guess])
        popt, pcov = curve_fit(S21_mag_fit, freqs_around_peak, S21_mag_around_peak, p0=init_guesses)
        QR = popt[1]
        QC = popt[2]
        QI = 1 / ((1 / QR) - (1 / QC))

        Q_Values = [QR, QC, QI]

        return Q_Values

    def get_three_dB_BW(self) -> float:
        """Get the 3dB BW from the peak in the data."""
        spline = UnivariateSpline(self.freqs, volts_to_db(self.S21_mag) + 3.0, s=0)
        return abs(spline.roots()[1] - spline.roots()[0])
