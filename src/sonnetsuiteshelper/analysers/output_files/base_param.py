from abc import ABC, abstractmethod
from typing import Literal, Self

from matplotlib import pyplot as plt
from matplotlib.pyplot import Axes
from numpy.typing import NDArray

from .. import utils


class SParamOutput(ABC):
    """SParamOutput."""

    @abstractmethod
    def _Sxx_mag(self, port1: int, port2: int) -> NDArray:
        pass

    @abstractmethod
    def _Sxx_mag_dB(self, port1: int, port2: int) -> NDArray:
        pass

    @classmethod
    @abstractmethod
    def from_spreadsheet(
        cls,
        filename: str,
        number_of_ports: int,
        freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"],
        file_path: str | None = None,
    ) -> Self:
        pass

    def __init__(
        self,
        filename: str,
        number_of_ports: int,
        freqs: NDArray,
        freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"],
    ) -> None:
        self.filename = filename
        self.number_of_ports: int = number_of_ports
        self.ports: list[int] = list(range(1, number_of_ports + 1))

        self._freqs_Hz = utils.freq_unit_change(freqs, freq_unit, "Hz")
        self._freq_unit = freq_unit

    def get_freqs(
        self,
        freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"] = "Hz",
    ) -> NDArray:
        """Get the frequencies.

        KwArgs
        ------
        freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"] = "Hz"
            The unit to return the frequencies in. Default is `Hz`.
        """
        if freq_unit == "Hz":
            return self._freqs_Hz

        return utils.freq_unit_change(self._freqs_Hz, "Hz", freq_unit)

    def _check_ports(self, port1: int, port2: int) -> None:
        """Check the ports exist."""
        if not isinstance(port1, int):
            raise TypeError(f"port1 should be of type int, found type `{type(port1)}`.")
        if not isinstance(port2, int):
            raise TypeError(f"port2 should be of type int, found type `{type(port2)}`.")

        if port1 not in self.ports:
            raise ValueError(f"Tried to assign port1 to `{port1}` but this port does not exist. port should be in {self.ports}.")
        if port2 not in self.ports:
            raise ValueError(f"Tried to assign port2 to `{port1}` but this port does not exist. port should be in {self.ports}.")

    def Sxx_mag(self, port1: int, port2: int) -> NDArray:
        self._check_ports(port1, port2)
        return self._Sxx_mag(port1, port2)

    def Sxx_mag_dB(self, port1: int, port2: int) -> NDArray:
        self._check_ports(port1, port2)
        return self._Sxx_mag_dB(port1, port2)

    def plot_freq_Sxx(
        self,
        port1: int,
        port2: int,
        freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"] = "Hz",
        Sxx_unit: Literal["mag", "mag_dB"] = "mag_dB",
        freq_range: tuple[float, float] | None = None,
        Sxx_range: tuple[float, float] | None = None,
        fig_ax: Axes | None = None,
        **kwargs,
    ) -> None:
        """TODO docstring."""
        x_data = self.get_freqs(freq_unit=freq_unit)

        match Sxx_unit:
            case "mag":
                y_data = self.Sxx_mag(port1, port2)
            case "mag_dB":
                y_data = self.Sxx_mag_dB(port1, port2)
            case _:
                accepted_Sxx_units = ["mag", "mag_dB"]
                raise ValueError(f"Invalid Sxx unit. Should be one of: {accepted_Sxx_units}.")

        title = f"File = {self.filename}"
        col = kwargs.pop("color", None)
        s = kwargs.pop("s", 0.5)
        alpha = kwargs.pop("alpha", 0.3)
        linewidth = kwargs.pop("linewidth", 0.2)
        label_str = kwargs.pop("label", None)

        x_label = f"frequency {freq_unit}"
        y_label = f"S{port1}{port2}_{Sxx_unit}"

        # If a matplotlib figure axes is defined just plot the data to that.
        if fig_ax:
            fig_ax.scatter(x_data, y_data, s=s, color=col, label=label_str, **kwargs)
            fig_ax.plot(x_data, y_data, linewidth=linewidth, alpha=alpha, color=col, **kwargs)
            fig_ax.set_xlabel(xlabel)
            fig_ax.set_ylabel(y_label)
            if Sxx_range:
                fig_ax.set_ylim(Sxx_range)
            if freq_range:
                fig_ax.set_ylim(freq_range)
            return

        fig = plt.figure(title)
        rows = 1
        cols = 1
        grid = plt.GridSpec(rows, cols)
        ax0 = plt.subplot(grid[0, 0])
        ax0.scatter(x_data, y_data, s=s, color=col, label=label_str, **kwargs)
        ax0.plot(x_data, y_data, linewidth=linewidth, alpha=alpha, color=col, **kwargs)

        ax0.set_title(title, loc="left")
        ax0.set_xlabel(x_label)
        ax0.set_ylabel(y_label)
        ax0.grid(alpha=0.3)
        fig.show()
