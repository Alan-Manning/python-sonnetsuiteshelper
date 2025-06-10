from pathlib import Path
from typing import Literal, Self

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from .. import utils
from .base_param import SParamOutput


class SParamRealImagOutput(SParamOutput):
    """SParamRealImagOutput."""

    def __init__(
        self,
        filename: str,
        number_of_ports: int,
        freqs: NDArray,
        freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"],
        reals_dict: dict[tuple[int, int], NDArray],
        imags_dict: dict[tuple[int, int], NDArray],
    ) -> None:
        super().__init__(filename, number_of_ports, freqs, freq_unit)
        self._reals_dict = reals_dict
        self._imags_dict = imags_dict

    def _Sxx_mag(self, port1: int, port2: int) -> NDArray:
        """Get the Sxx mag."""
        self._check_ports(port1, port2)

        real = self._reals_dict[(port1, port2)]
        imag = self._imags_dict[(port1, port2)]

        Sxx_mag = np.array(np.abs(real + 1j * imag))
        return Sxx_mag

    def _Sxx_mag_dB(self, port1: int, port2: int) -> NDArray:
        """Get the Sxx mag in decibells."""
        self._check_ports(port1, port2)
        S_xx_mag_dB = utils.volts_to_db(self.Sxx_mag(port1, port2))
        return S_xx_mag_dB

    @classmethod
    def from_spreadsheet(
        cls,
        filename: str,
        number_of_ports: int,
        freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"],
        file_path: str | None = None,
    ) -> Self:
        """Construct a SParamRealImagOutput object from a spreadsheet type file
        output.

        Parameters
        ----------
        filename: str
            The filename of the output file.

        number_of_ports: int,
            The number of ports in the output file.

        freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"],
            The unit of the frequencies in the output file.

        KwArgs
        ------
        file_path: str | None = None,
            The path to the directory containing the output file.
        """
        # checking all the args
        accepted_freq_units = ["Hz", "KHz", "MHz", "GHz", "THz", "PHz"]
        if freq_unit not in accepted_freq_units:
            raise ValueError(f"freq_unit `{freq_unit}` is not valid. valid units are: {accepted_freq_units}")

        if not isinstance(number_of_ports, int):
            raise TypeError(f"number_of_ports should be of type int, found type `{type(number_of_ports)}`.")

        ports: list[int] = list(range(1, number_of_ports + 1))

        if file_path is None:
            file_path = ""

        file = Path(file_path, filename)
        file_exists = Path.is_file(file)

        if not file_exists:
            raise FileNotFoundError(f"Unable to find file: {file}")

        # get the column names
        csv_col_names = [f"Frequency ({freq_unit})"]
        for p1 in ports:
            for p2 in ports:
                real = f"RE[S{p1}{p2}]"
                imag = f"IM[S{p1}{p2}]"
                csv_col_names.append(real)
                csv_col_names.append(imag)

        skip_row = 2
        file_data = pd.read_csv(file, names=csv_col_names, skiprows=skip_row)

        while isinstance(file_data["Frequency (GHz)"][0], str):
            file_data = pd.read_csv(file, names=csv_col_names, skiprows=skip_row)
            skip_row += 1

        freqs = np.array(file_data[f"Frequency ({freq_unit})"])
        reals_dict = {}
        imags_dict = {}
        for p1 in ports:
            for p2 in ports:
                reals_dict[(p1, p2)] = file_data[f"RE[S{p1}{p2}]"]
                imags_dict[(p1, p2)] = file_data[f"IM[S{p1}{p2}]"]

        return cls(
            filename,
            number_of_ports,
            freqs,
            freq_unit,
            reals_dict,
            imags_dict,
        )
