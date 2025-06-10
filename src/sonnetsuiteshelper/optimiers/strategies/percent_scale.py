from typing import Literal

from matplotlib.axes import Axes

from ...utils import round_to_sonnet_mesh_size
from .base import OptimiserStrategy


class PercentScale(OptimiserStrategy):
    """Get the next variable value from simply adding/subtracting to the
    previous variable value by some adjust adjust strength multiplied by the
    delta between the last output value and the fnal desired output value. i.e.
    next = last +- (delta_from_desired*adjust_strength).

    This result is then rounded to the nearest sonnet mesh grid point.
    """

    @property
    def name(self) -> str:
        """The name property."""
        return "PercentScale"

    def plot(
        self,
        fig_ax: Axes,
        variable_param_values: list[float],
        desired_output_param_values: list[float],
    ) -> None:
        pass

    def get_next_variable_param_value(
        self,
        current_desired_output_param_value: float,
        desired_output_param_value: float,
        variable_param_values: list[float],
        desired_output_param_values: list[float],
        correlation: Literal[+1, -1],
        sonnet_mesh_size: float,
    ) -> float:
        """Get the next varaible param value."""
        delta_from_desired = abs(current_desired_output_param_value - desired_output_param_value)
        adjust_strength = 0.002
        delta_in_variable_param = adjust_strength * delta_from_desired

        if current_desired_output_param_value > desired_output_param_value:
            new_value = variable_param_values[-1] - (correlation * delta_in_variable_param)
        else:
            new_value = variable_param_values[-1] + (correlation * delta_in_variable_param)

        return round_to_sonnet_mesh_size(new_value, sonnet_mesh_size)
