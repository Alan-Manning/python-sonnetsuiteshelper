from dataclasses import dataclass
from typing import Literal

from ..strategies import OptimiserStrategy


@dataclass
class OptimiserSettings:
    """OptimiserSettings.
    freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"]
    number_of_ports: int
    output_file_format: Literal["Spreadsheet"]

    varaible_param_name: str
    desired_output_param: str
    desired_output_param_value: float
    desired_output_param_value_tolerence_percent: float
    correlation: Literal["+", "-"]
    optimisation_strategy: OptimiserStrategy
    min_value_for_variable_param: float | None = None
    max_value_for_variable_param: float | None = None
    sonnet_mesh_size: float = 1.0

    instance variables
    ------------------
    varaible_param_name: str
        The name of the parameter that should be varied by the optimiser
        to achieve the desired result.

    desired_output_param : str
        The variable output the optimiser should be optimising for. e.g.
        if trying to get a resonant frequency of 2GHz, then this argument
        will be `desired_output_param="f0"`. The values accepted are dependent
        on the Optimiser being used.

    desired_output_param_value: float
        The value of the desired_output_param. e.g. if trying to
        resonant frequency of 2GHz, then this argument will be
        `desired_output_param_value=2.0e9`.

    desired_output_param_value_tolerence_percent: float
        This is the percentage tolerance around the desired_output_param_value.
        eg. if trying to get resonant frequency of 2GHz +- 1%, then this
        argument will be `desired_output_param_value_tolerence_percent = 0.01`.

    correlation: Literal["+", "-"],
        The correlation between the variable parameter and the desired
        output param. This accepts str values "+" or "-".
        If an `increase` in the `variable_param_value` results in an `increase`
        of the `desired_output_param`, then this should be `"+"`.
        If an `increase` in the `variable_param_value` results in a `decrease`
        of the `desired_output_param`, Then this should be `"-"`.

    min_value_for_variable_param: float | None = None,
        The min value the variable param can take. Default None will not do
        anything. When specified this will clamp the min value.

    max_value_for_variable_param: float | None = None,
        The max value the variable param can take. Default None will not do
        anything. When specified this will clamp the max value.

    sonnet_mesh_size : float = 1.0
        Default=1.0. The mesh size in sonnet. This is the smallest change
        possible in the varaible parameter that will result in a different
        file being produced.
    """

    freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"]
    number_of_ports: int
    output_file_format: Literal["Spreadsheet"]

    varaible_param_name: str
    desired_output_param: str
    desired_output_param_value: float
    desired_output_param_value_tolerence_percent: float
    correlation: Literal["+", "-"]
    optimisation_strategy: OptimiserStrategy
    min_value_for_variable_param: float | None = None
    max_value_for_variable_param: float | None = None
    sonnet_mesh_size: float = 1.0
