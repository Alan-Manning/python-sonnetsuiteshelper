import numpy as np


def round_to_sonnet_mesh_size(value: float, sonnet_mesh_size: float) -> float:
    """Round the input value to the nearest sonnet_mesh_size step."""
    rounded_result = np.round(float(value) / sonnet_mesh_size) * sonnet_mesh_size
    return rounded_result
