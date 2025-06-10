from collections.abc import KeysView
from pathlib import Path


class GeneralMetalKeyError(Exception):
    """Exception raised when the general metal does not have the correct form.

    Parameters
    ----------
    metal_name: str
        The name of the general metal to edit.

    keys: KeysView
        The keys in the general metal to edit.

    keys: list[str]
        The required keys for the general metal to edit.
    """

    def __init__(self, metal_name: str, keys: KeysView, required_keys: list[str]) -> None:
        self.required_keys = required_keys
        self.keys = keys
        self.metal_name = metal_name
        self.message = f"The `{self.metal_name}` general metal to edit does not have the correct keys. Keys needed are `{self.required_keys}`. The keys present are: {self.keys}."
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class GeneralMetalNotFoundError(Exception):
    """Exception raised when the general metal is not found in the sonnet file.

    Parameters
    ----------
    metal_name: str
        The name of the general metal to edit.

    file: Path
        The file the general metal to edit was absent from.
    """

    def __init__(self, metal_name: str, file: Path) -> None:
        self.metal_name = metal_name
        self.file = file
        self.message = f"General metal to edit `{self.metal_name}` not found in file `{self.file}`."
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class AdaptiveSweepKeyError(Exception):
    """Exception raised when the adaptive sweep does not have the correct form.

    Parameters
    ----------
    keys: KeysView
        The keys in the adaptive sweep to edit.

    required_keys: list[str]
        The keys in the adaptive sweep to edit.
    """

    def __init__(self, keys: KeysView, required_keys: list[str]) -> None:
        self.required_keys = required_keys
        self.keys = keys
        self.message = f"The adaptive sweep to edit does not have the correct keys. Keys needed are {self.required_keys}. The keys present are: {self.keys}."
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class AdaptiveSweepNotFoundError(Exception):
    """Exception raised when the adaptive sweep is not found in the sonnet
    file.

    Parameters
    ----------
    file: Path
        The file the adaptive sweep was absent from.
    """

    def __init__(self, file: Path) -> None:
        self.file = file
        self.message = f"Adaptive sweep to edit not found in file `{self.file}`."
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class LinearSweepKeyError(Exception):
    """Exception raised when the linear sweep does not have the correct form.

    Parameters
    ----------
    keys: KeysView
        The keys in the linear sweep to edit.

    required_keys: list[str]
        The required keys in the linear sweep to edit.
    """

    def __init__(self, keys: KeysView, required_keys: list[str]) -> None:
        self.required_keys = required_keys
        self.keys = keys
        self.message = f"The linear sweep to edit does not have the correct keys. Keys needed are {self.required_keys}. The keys present are: {self.keys}."
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class LinearSweepNotFoundError(Exception):
    """Exception raised when the linear sweep is not found in the sonnet file.

    Parameters
    ----------
    file: Path
        The file the linear sweep was absent from.
    """

    def __init__(self, file: Path) -> None:
        self.file = file
        self.message = f"linear sweep to edit not found in file `{self.file}`."
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class EmOptionsKeyError(Exception):
    """Exception raised when the em options does not have the correct form.

    Parameters
    ----------
    key: str
        The keys in the em options to edit.

    accepted_keys: list[str]
        The keys in em options to edit accepts.
    """

    def __init__(self, key: str, accepted_keys: list[str]) -> None:
        self.key = key
        self.accepted_keys = accepted_keys
        self.message = f"Can't interpret key '{self.key}' in em options to edit. Accepted keys are: {self.accepted_keys}"
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class EmOptionsNotFoundError(Exception):
    """Exception raised when the em options is not found in the sonnet file.

    Parameters
    ----------
    key: str
        The em option key to edit.

    file: Path
        The file the em option key was absent from.
    """

    def __init__(self, key: str, file: Path) -> None:
        self.key = key
        self.file = file
        self.message = f"em_options_to_edit '{self.key}' not found in file `{self.file}`."
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class ParamNotFoundError(Exception):
    """Exception raised when the param is not found in the sonnet file.

    Parameters
    ----------
    param: str
        The name of the absent parameter.

    file: Path
        The file the parameter was absent from.
    """

    def __init__(self, param: str, file: Path) -> None:
        self.param = param
        self.file = file
        self.message = f"Parmeter `{self.param}` not found in file `{self.file}`."
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
