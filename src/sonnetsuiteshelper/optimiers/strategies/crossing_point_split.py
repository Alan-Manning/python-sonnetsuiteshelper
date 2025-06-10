from typing import Literal

import numpy as np
from matplotlib.axes import Axes

from ...utils import round_to_sonnet_mesh_size
from .base import OptimiserStrategy
from .percent_scale import PercentScale


class CrossingPointSplit(OptimiserStrategy):
    """Get the next variable value by getting the variable param values where
    the desired output param values are either side of the desired output param
    value. Then take the crossing point between those variable param values.
    Esentially this lin fits the two points either side of the desired.

    This result is then rounded to the nearest sonnet mesh grid point.
    """

    @property
    def name(self) -> str:
        return "CrossingPointSplit"

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

        y_data_offset = y_data - desired_output_param_value

        x_data_above: list[float] = []
        y_data_above: list[float] = []
        x_data_below: list[float] = []
        y_data_below: list[float] = []

        min_x_above: float = 0
        min_y_above: float = np.inf
        max_x_below: float = 0
        max_y_below: float = -np.inf

        for x, yo in zip(x_data, y_data_offset, strict=True):
            if yo > 0:
                y_data_above.append(yo)
                x_data_above.append(x)
                if yo < min_y_above:
                    min_y_above = yo
                    min_x_above = x
            else:
                y_data_below.append(yo)
                x_data_below.append(x)
                if yo > min_y_above:
                    max_y_below = yo
                    max_x_below = x

        if (len(y_data_above) == 0) or (len(y_data_below) == 0):
            raise RuntimeError(
                f"Cannot use {self.name} OptimiserStrategy because there are not two points either side of the desired_output_param_value {desired_output_param_value}."
            )

        fit_y_data = [min_y_above, max_y_below]
        fit_x_data = [min_x_above, max_x_below]

        poly_fit = np.polyfit(fit_y_data, fit_x_data, deg=1)
        poly_func = np.poly1d(poly_fit)
        new_value = poly_func(0)

        # If the value returned from linear fit has not already been simulated then retrun.
        return round_to_sonnet_mesh_size(new_value, sonnet_mesh_size)

    def plot(
        self,
        fig_ax: Axes,
        variable_param_values: list[float],
        desired_output_param_values: list[float],
    ) -> None:
        """Plot the OptimiserStrategy."""

        x_data = np.array(variable_param_values)
        y_data = np.array(desired_output_param_values)

        y_data_offset = y_data - desired_output_param_value

        x_data_above: list[float] = []
        y_data_above: list[float] = []
        x_data_below: list[float] = []
        y_data_below: list[float] = []

        min_x_above: float = 0
        min_y_above: float = np.inf
        max_x_below: float = 0
        max_y_below: float = -np.inf

        for x, yo in zip(x_data, y_data_offset, strict=True):
            if yo > 0:
                y_data_above.append(yo)
                x_data_above.append(x)
                if yo < min_y_above:
                    min_y_above = yo
                    min_x_above = x
            else:
                y_data_below.append(yo)
                x_data_below.append(x)
                if yo > min_y_above:
                    max_y_below = yo
                    max_x_below = x

        if (len(y_data_above) == 0) or (len(y_data_below) == 0):
            raise RuntimeError(
                f"Cannot use {self.name} OptimiserStrategy because there are not two points either side of the desired_output_param_value {desired_output_param_value}."
            )

        fit_y_data = [min_y_above, max_y_below]
        fit_x_data = [min_x_above, max_x_below]

        poly_fit = np.polyfit(fit_y_data, fit_x_data, deg=1)
        poly_func = np.poly1d(poly_fit)

        NO_OF_POINTS = 10

        y_plot_values = np.linspace(min(fit_y_data), max(fit_y_data), NO_OF_POINTS)
        x_plot_values = poly_func(y_plot_values)

        fig_ax.plot(
            x_plot_values,
            y_plot_values,
        )
