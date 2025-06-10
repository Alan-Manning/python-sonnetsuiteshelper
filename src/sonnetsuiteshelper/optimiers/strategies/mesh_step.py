from typing import Literal

from matplotlib.axes import Axes

from ...utils import round_to_sonnet_mesh_size
from .base import OptimiserStrategy


class MeshStep(OptimiserStrategy):
    """Get the next variable value by changing the curent variable_param_value
    by the sonnet file mesh size in the direction of the correlation.

    This follows similar logic to the PercentScale stragety but only
    increases or decreases the value by the sonnet_mesh_size.
    """

    @property
    def name(self) -> str:
        """The name property."""
        return "MeshStep"

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

        if current_desired_output_param_value > desired_output_param_value:
            new_value = variable_param_values[-1] + (correlation * sonnet_mesh_size)
        else:
            new_value = variable_param_values[-1] - (correlation * sonnet_mesh_size)

        return new_value
