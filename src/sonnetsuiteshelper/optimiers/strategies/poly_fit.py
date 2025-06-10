from typing import Literal

import numpy as np
from matplotlib.axes import Axes

from ...utils import round_to_sonnet_mesh_size
from .base import OptimiserStrategy
from .mesh_step import MeshStep
from .percent_scale import PercentScale


class PolyFit(OptimiserStrategy):
    """Get the next variable value by performing a polynomial fit the data.
    This is identical to the LinFit OptimiserStrategy in the case of degree 2.

    This result is then rounded to the nearest sonnet mesh grid point.

    Parameters
    ----------
    degree: int
        The degree of the polynomial fit function.
    """

    def __init__(self, degree: int) -> None:
        """
        Parameters
        ----------
        degree: int
            The degree of the polynomial fit function.
        """
        if not isinstance(degree, int):
            raise TypeError(f"degree should be of type int. not of type {type(degree)}")

        self.poly_degree = degree

    @property
    def name(self) -> str:
        return "PolyFit"

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
        poly_fit = np.polyfit(y_data, x_data, deg=self.poly_degree)
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
        poly_fit = np.polyfit(y_data, x_data, deg=self.poly_degree)
        poly_func = np.poly1d(poly_fit)

        y_min = y_data.min()
        y_max = y_data.max()
        NO_OF_POINTS = 50

        y_plot_values = np.linspace(y_min, y_max, NO_OF_POINTS)
        x_plot_values = poly_func(y_plot_values)

        fig_ax.plot(
            x_plot_values,
            y_plot_values,
        )
