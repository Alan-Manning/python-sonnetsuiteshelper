import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.gridspec import GridSpec

from ...analysers.output_files.s_param import SParamRealImagOutput
from ...analysers.single_resonator import SParamSingleResonatorAnalyser
from .base import SingleParamOptimiser
from .optimiser_settings import OptimiserSettings


class SParamSingleResonatorOptimiser(SingleParamOptimiser):
    """Optimiser for Sonnet files using the SonnetCSVOutputFile.

    This takes in an initial .son file and .csv output from running that
    sonnet file and will try to optimise that file for a specific value
    within some defined tolerance.
    """

    def __init__(
        self,
        unique_name: str,
        batch_1_filename: str,
        batch_1_son_file_path: str,
        batch_1_output_file_path: str,
        init_variable_param_value: float,
        optimiser_settings: OptimiserSettings,
        ignore_loading_cache: bool = False,
    ) -> None:
        super().__init__(
            unique_name,
            batch_1_filename,
            batch_1_son_file_path,
            batch_1_output_file_path,
            init_variable_param_value,
            optimiser_settings,
            ignore_loading_cache,
        )

    def _check_desired_output_param(self, desired_output_param: str) -> None:
        accepted_desired_output_params = ["QR", "QC", "QI", "f0", "three_dB_BW"]
        if desired_output_param in accepted_desired_output_params:
            return
        raise ValueError(f"Cannot optimise for `{desired_output_param}`. Can only optimise for {accepted_desired_output_params}")

    def _analyse_batch(
        self,
        filename: str,
        file_path: str,
        desired_output_param: str,
    ) -> float:
        match self.output_file_format:
            case "Spreadsheet":
                s_param_out = SParamRealImagOutput.from_spreadsheet(
                    filename + ".csv",
                    self.number_of_ports,
                    self.freq_unit,
                    file_path=file_path,
                )
            case _:
                raise ValueError(f"Could not analyse batch with file format {self.output_file_format}")

        single_resonator_analyser = SParamSingleResonatorAnalyser(s_param_out)

        match desired_output_param:
            case "QR":
                return single_resonator_analyser.get_Q_values().QR
            case "QC":
                return single_resonator_analyser.get_Q_values().QC
            case "QI":
                return single_resonator_analyser.get_Q_values().QI
            case "f0":
                return single_resonator_analyser.get_resonant_freq()
            case "three_dB_BW":
                return single_resonator_analyser.get_three_dB_BW()
            case _:
                raise ValueError(f"Error, cannot optimise for {desired_output_param}")

    def plot(
        self,
        fig_ax: Axes | None = None,
        set_axis_labels: bool = True,
        plot_next_variable_param_value: bool = True,
        plot_strategy: bool = True,
    ) -> None:
        """Plot the current results of the optimiser.

        Parameters
        ----------
        fig_ax: Axes | None = None
            Default value `None` will generate a new figure. When specified
            this should be a figure axes of type `Axes` and the result will be
            ploted on this.

        set_axis_labels: bool = True,
            Default `True` will set the figure axes labels but will not when
            set to False.

        plot_next_variable_param_value: bool = True,
            Default `True` will plot the next value to be simulated to the
            figure axes but will not when set to False.

        plot_strategy: bool = True,
            Default `True` will attempt to plot the strategy that gives the
            next value to be simulated to the figure axes but will not when
            set to False.
        """

        FACE_COLOR_FOR_OPTIMISED = "#b4f7ab"
        FACE_COLOR_FOR_NOT_OPTIMISED = "#fcc7bd"

        x_data = np.array(self.variable_param_values)
        x_label = self.variable_param_name

        y_data = np.array(self.desired_output_param_values)
        y_label = self.desired_output_param

        # Setting up a figure if axes were not specified.
        if fig_ax is None:
            title = f"{self.name} - {self.desired_output_param} vs {self.variable_param_name}"
            fig = plt.figure(title)
            rows = 1
            cols = 1
            grid = GridSpec(rows, cols)
            ax = plt.subplot(grid[0, 0])
        else:
            fig = None
            ax = fig_ax

        # Colors for the data such that its clearer when plotted with values that are close together.
        phi = np.linspace(0, np.pi, len(x_data))
        rgb_cycle = (
            np.stack(
                (
                    np.cos(phi),
                    np.cos(phi + 2 * np.pi / 3),
                    np.cos(phi - 2 * np.pi / 3),
                )
            ).T
            + 1
        ) * 0.5

        # Plotting the data from the optimiser.
        for i, (x, y) in enumerate(zip(x_data, y_data, strict=True)):
            ax.scatter(x, y, s=5, color=rgb_cycle[i])
            ax.annotate(f"{i+1}", (x, y))

        # Plotting the desired_output_param_value.
        ax.axhline(y=self.desired_output_param_value)

        # Setting the plot looks based on if the optimiser is finished or not.
        if self.has_reached_optimisation():
            ax.set_facecolor(FACE_COLOR_FOR_OPTIMISED)
            ax.text(
                0.5,
                0.5,
                f"FINISHED AT BATCH {self.current_batch_no - 1}",
                transform=ax.transAxes,
                color="gray",
                alpha=0.6,
                ha="center",
                va="center",
            )
        else:
            ax.set_facecolor(FACE_COLOR_FOR_NOT_OPTIMISED)

        # plotting the next value if kwarg and if optimiser hasnt finished.
        if plot_next_variable_param_value and (not self.has_reached_optimisation()):
            ax.scatter(
                self.next_variable_param_value,
                self.desired_output_param_value,
                s=50,
                color="red",
                marker="x",
            )
            ax.annotate(f"{i+1}", (x, y))
        # plotting the optimiser strategy if possible
        if plot_strategy:
            self.optimisation_strategy.plot(
                ax,
                self.variable_param_values,
                self.desired_output_param_values,
            )

        if set_axis_labels:
            ax.set_xlabel(f"{x_label}")
            ax.set_ylabel(f"{y_label}")

        ax.grid(alpha=0.1, color="black")

        if fig is not None:
            fig.show()

        return
