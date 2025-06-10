from typing import Literal

import numpy as np
from matplotlib.axes import Axes

from ...utils import round_to_sonnet_mesh_size
from .base import OptimiserStrategy
from .mesh_step import MeshStep
from .percent_scale import PercentScale


class LinFit(OptimiserStrategy):
    """Get the next variable value by lin fitting the data. This makes a linear
    fit and then gets the variable value that results in an intersection with
    the desired_output_param_value.

    This result is then rounded to the nearest sonnet mesh grid point.
    """

    @property
    def name(self) -> str:
        return "LinFit"

    def get_next_variable_param_value(
        self,
        current_desired_output_param_value: float,
        desired_output_param_value: float,
        variable_param_values: list[float],
        desired_output_param_values: list[float],
        correlation: Literal[+1, -1],
        sonnet_mesh_size: float,
    ) -> float:
        # If there are less than 4 points
        if len(variable_param_values) <= 3:
            new_value = PercentScale().get_next_variable_param_value(
                current_desired_output_param_value,
                desired_output_param_value,
                variable_param_values,
                desired_output_param_values,
                correlation,
                sonnet_mesh_size,
            )
            return new_value

        x_data = np.array(variable_param_values)
        y_data = np.array(desired_output_param_values)
        poly_fit = np.polyfit(y_data, x_data, deg=1)
        poly_func = np.poly1d(poly_fit)
        new_value = poly_func(desired_output_param_value)

        # If the value returned from linear fit has not already been simulated then retrun.
        if new_value not in variable_param_values:
            return round_to_sonnet_mesh_size(new_value, sonnet_mesh_size)

        # If the linear fit value has already been simulated then try linear fit.
        new_value = PercentScale().get_next_variable_param_value(
            current_desired_output_param_value,
            desired_output_param_value,
            variable_param_values,
            desired_output_param_values,
            correlation,
            sonnet_mesh_size,
        )
        if new_value not in variable_param_values:
            return new_value

        # if the percent scale has already been simulated then try mesh step size.
        if new_value in variable_param_values:
            new_value = MeshStep().get_next_variable_param_value(
                current_desired_output_param_value,
                desired_output_param_value,
                variable_param_values,
                desired_output_param_values,
                correlation,
                sonnet_mesh_size,
            )
        if new_value not in variable_param_values:
            return new_value

        raise RuntimeError(f"OptimiserStrategy {self.name} was unable to find appropriate next variable_param_value.")

    def plot(
        self,
        fig_ax: Axes,
        variable_param_values: list[float],
        desired_output_param_values: list[float],
    ) -> None:
        """Plot the OptimiserStrategy."""

        x_data = np.array(variable_param_values)
        y_data = np.array(desired_output_param_values)
        poly_fit = np.polyfit(y_data, x_data, deg=1)
        poly_func = np.poly1d(poly_fit)

        # new_value = poly_func(desired_output_param_value)
        y_min = y_data.min()
        y_max = y_data.max()
        NO_OF_POINTS = 50

        y_plot_values = np.linspace(y_min, y_max, NO_OF_POINTS)
        x_plot_values = poly_func(y_plot_values)

        fig_ax.plot(
            x_plot_values,
            y_plot_values,
        )
