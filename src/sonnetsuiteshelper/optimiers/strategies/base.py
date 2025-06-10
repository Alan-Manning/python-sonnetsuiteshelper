from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Literal

from matplotlib.axes import Axes


class OptimiserStrategy(ABC):
    """OptimiserStrategy.

    abstract property
    -----------------
    name() -> str

    abstract method
    ---------------
    def get_next_variable_param_value() -> float:
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def get_next_variable_param_value(
        self,
        current_desired_output_param_value: float,
        desired_output_param_value: float,
        variable_param_values: list[float],
        desired_output_param_values: list[float],
        correlation: Literal[+1, -1],
        sonnet_mesh_size: float,
    ) -> float:
        pass

    @abstractmethod
    def plot(
        self,
        fig_ax: Axes,
        variable_param_values: list[float],
        desired_output_param_values: list[float],
    ) -> None:
        pass
