import re
from collections.abc import Mapping
from logging import debug
from pathlib import Path
from typing import Literal

from . import errors


def generate_file_like(
    base_filename: str,
    output_filename: str,
    base_file_path: str = "",
    output_file_path: str = "",
    output_filename_prefix: str = "",
    output_filename_suffix: str = "",
    params_to_edit: Mapping[str, str | float | int] | None = None,
    general_metals_to_edit: Mapping[str, dict[Literal["Rdc", "Rrf", "Xdc", "Ls"], float]] | None = None,
    adaptive_sweeps_to_edit: Mapping[Literal["sweep_min", "sweep_max", "target_freqs"], float | int] | None = None,
    linear_sweeps_to_edit: Mapping[Literal["sweep_min", "sweep_max", "step_size"], float | int] | None = None,
    em_options_to_edit: Mapping[Literal["speed"], Literal[0, 1, 2]] | None = None,
    silent: bool = False,
    ignore_overwrite_warning: bool = False,
) -> None:
    """This generates a Sonnet file like the base file specified. This will
    take in a series of values or other elements to further modify the Sonnet
    file to be produced.

    Parameters
    ----------
    base_filename: str
        This is the name of the base file, this will assume a ".son" file
        extention if this is not included in the base file name. This will be
        used to create the new Sonnet file. This can include the path of the
        file if it does not exist in the same directory as the python script.

    output_filename: str
        This is the name for the output file to be generated. If this does not
        have a ".son" file extention already, one will be added. If a file with
        this name already exists then its contents will be overwritten.

    KwArgs
    ------
    output_file_path: str
        This is the directory that the output file should be saved to.
        By default this is a blank string which will save the file in the same
        directory as the script. When specified the output file will be saved
        to this directory. If this directory does not already exist it will be
        created.

    output_filename_prefix: str
        This is a string to add to the beggining of the filename. Default is a
        blank string.

    output_filename_suffix: str
        This is a string to add to the end of the filename. Default is a
        blank string.

    params_to_edit: Mapping[str, str | float | int] | None = None
        This is a dictionary that has keys of parameter names and values of the
        values those parameters should take. Note the values must be of type
        float or int. This can take any number of key and value pairs. If there
        is any parameter that isnt in the base file that exists in this dict
        then this will raise an error and will not continue. An example
        dictionary to be passed would take the form:
        >>> Params_to_edit = {
        ...     "Length_var_1" : 400,
        ...     "Length_var_2" : 250,
        ...     "Length_var_3" : 1975,
        ...     ...
        ... }

    general_metals_to_edit: Mapping[str, dict[Literal["Rdc", "Rrf", "Xdc", "Ls"], float]] | None = None
        This is a dictionary that has keys of general metal names and values of
        dictionarys with "Rdc", "Rrf", "Xdc", "Ls" key names and values with
        values for those keys. Note those keys must exist in the dict for each
        general metal to edit. Any number of general metals can be passed. If
        there is any metal in this dictionary that doesn't exist in the base
        file, or if that metal is there but has the wrong dict keys, this will
        raise an error and will not continue.
        An example dict to be passed would take the form:
        >>> gen_mets_edits = {
        ...     "gen_met_1": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8},
        ...     "gen_met_2": {"Rdc": 1e-08, "Rrf": 14e-8, "Xdc": 0, "Ls": 0.003},
        ...     ...
        ... }

    adaptive_sweeps_to_editMapping[Literal["sweep_min", "sweep_max", "target_freqs"], float | int] | None = None
        This is a dictionary that has keys of "sweep_min", "sweep_max",
        "target_freqs" and values of the values for those keys.
        An example dict to be passed would take the form:
        >>> adaptive_sweep = {
        ...     "sweep_min" : 1.0,
        ...     "sweep_max" : 5.0,
        ...     "target_freqs" : 500,
        ... }

    linear_sweeps_to_edit: Mapping[Literal["sweep_min", "sweep_max", "step_size"], float | int] | None = None
        This is a dictionary that has keys of "sweep_min", "sweep_max",
        "step_size" and values of the values for those keys.
        An example dict to be passed would take the form:
        >>> linear_sweep = {
        ...     "sweep_min" : 1.0,
        ...     "sweep_max" : 5.0,
        ...     "step_size" : 0.1,
        ... }

    em_options_to_edit: Mapping[Literal["speed"], Literal[0, 1, 2]] | None = None
        This is a dictionary that has keys of "speed" (which is either 0, 1, 2,
        this corrosponds to "Speed Memory" option in Sonnet EM options).
        >>> em_opts = {
        ...     "speed" : 1,
        ... }

    silent: bool = False
        Mute the output from makingg files.

    ignore_overwrite_warning: bool = False,
        Ignore warnings about overwriting files.

    Warnings
    --------
    If a file with this name already exists then its contents will be
    overwritten!
    """

    # if the basefile has no .son file extention add it.
    if base_filename[-4:] != ".son":
        base_filename = f"{base_filename}.son"

    # add the path for the basefile
    base_file = Path(base_file_path, base_filename)

    # check base_file exists
    if not base_file.is_file():
        raise FileNotFoundError(f"Unable to find file: {base_file}")

    # if .son file extention exists remove it. It is added next.
    if output_filename[-4:] == ".son":
        output_filename = output_filename[:-4]

    output_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"

    final_file_path = Path(output_file_path)

    # create the output directory, if exists ignore warning.
    final_file_path.mkdir(exist_ok=True, parents=True)

    final_file = final_file_path / output_filename

    if final_file.exists():
        user_input = input(f"Warning: `{final_file}` already exists.\nOverwrite file? y/[n]:").upper()
        if user_input not in ["Y", "YES", "YE"]:
            print(f"Skiped writing file\n\tname: {output_filename}\n\tpath: {output_file_path}")
            return

    with base_file.open() as f:
        contents = f.read()

    # If params dict not None then change vals
    if params_to_edit:
        for key, val in params_to_edit.items():
            pattern = re.compile(rf'VALVAR {key} LNG (\w+|"\w+"|\d+\.\d+) "Dim\. Param\."')

            if pattern.search(contents):
                replacement = f'VALVAR {key} LNG {val} "Dim. Param."'
                contents = pattern.sub(replacement, contents)
            else:
                raise errors.ParamNotFoundError(key, base_file)

    # If general_metals dict not None then change vals
    if general_metals_to_edit:
        keys_needed = ["Rdc", "Rrf", "Xdc", "Ls"]
        for metal_name, vals in general_metals_to_edit.items():
            # check that the correct keys are in the dict
            if not all(key in vals for key in keys_needed):
                raise errors.GeneralMetalKeyError(metal_name, vals.keys(), keys_needed)

            full_pattern = re.compile(r'MET "' + metal_name + r'" \d+ SUP( [+\-]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+\-]?\d+)?){4}')
            match = full_pattern.search(contents)
            if match:
                metal_match_string = match.group()

                Rdc = vals["Rdc"]
                Rrf = vals["Rrf"]
                Xdc = vals["Xdc"]
                Ls = vals["Ls"]

                values_pattern = re.compile(r"( [+\-]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+\-]?\d+)?){4}")
                values_to_put_in = f" {Rdc} {Rrf} {Xdc} {Ls}"

                new_metal_string = values_pattern.sub(values_to_put_in, metal_match_string)

                contents = full_pattern.sub(new_metal_string, contents)
            else:
                raise errors.GeneralMetalNotFoundError(metal_name, base_file)

    # If sweeps dict not None then change vals
    if adaptive_sweeps_to_edit:
        keys_needed = ["sweep_min", "sweep_max", "target_freqs"]
        # check that the correct keys are in the dict and if so do replacement
        if not all(key in adaptive_sweeps_to_edit for key in keys_needed):
            raise errors.AdaptiveSweepKeyError(adaptive_sweeps_to_edit.keys(), keys_needed)

        full_pattern = re.compile(r"FREQ \w+ AY ABS_ENTRY( (-)?[0-9]\d*(\.\d+)?){4}")
        match = full_pattern.search(contents)
        if match:
            abs_sweep_match_string = match.group()

            new_sweep_min = adaptive_sweeps_to_edit["sweep_min"]
            new_sweep_max = adaptive_sweeps_to_edit["sweep_max"]
            target_freqs = adaptive_sweeps_to_edit["target_freqs"]

            sweep_min_max_pattern = re.compile(r"ABS_ENTRY( (-)?[0-9]\d*(\.\d+)?){2}")
            sweep_min_max_replacement = f"ABS_ENTRY {new_sweep_min} {new_sweep_max}"
            new_abs_sweep_string = sweep_min_max_pattern.sub(sweep_min_max_replacement, abs_sweep_match_string)

            target_freqs_pattern = re.compile(r"(\d+)\D*$")
            target_freqs_replacement = f"{target_freqs}"
            new_abs_sweep_string = target_freqs_pattern.sub(target_freqs_replacement, new_abs_sweep_string)

            contents = full_pattern.sub(new_abs_sweep_string, contents)
        else:
            raise errors.AdaptiveSweepNotFoundError(base_file)

    # If sweeps dict not None then change vals
    if linear_sweeps_to_edit:
        keys_needed = ["sweep_min", "sweep_max", "step_size"]
        # check that the correct keys are in the dict and if so do replacement
        if not all(key in linear_sweeps_to_edit for key in keys_needed):
            raise errors.LinearSweepKeyError(linear_sweeps_to_edit.keys(), keys_needed)

        full_pattern = re.compile(r"FREQ \w+ \w+ SWEEP( (-)?[0-9]\d*(\.\d+)?){3}")
        match = full_pattern.search(contents)
        if match:
            linear_sweep_match_string = match.group()

            new_sweep_min = linear_sweeps_to_edit["sweep_min"]
            new_sweep_max = linear_sweeps_to_edit["sweep_max"]
            step_size = linear_sweeps_to_edit["step_size"]

            values_pattern = re.compile(r"( (-)?[0-9]\d*(\.\d+)?){3}")
            values_to_put_in = f" {new_sweep_min} {new_sweep_max} {step_size}"
            new_linear_sweep_string = values_pattern.sub(values_to_put_in, linear_sweep_match_string)

            contents = full_pattern.sub(new_linear_sweep_string, contents)
        else:
            raise errors.LinearSweepNotFoundError(base_file)

    # If em_options_to_edit dict not None then change vals
    if em_options_to_edit:
        keys_accepted = ["speed"]
        for key, val in em_options_to_edit.items():
            if key not in keys_accepted:
                raise errors.EmOptionsKeyError(key, keys_accepted)

            if key == "speed":
                pattern = re.compile(r"SPEED \d")

                if pattern.search(contents):
                    replacement = f"SPEED {val}"
                    contents = pattern.sub(replacement, contents)
                else:
                    raise errors.EmOptionsNotFoundError(key, base_file)

    # with final_file.open("w") as f:
    with open(final_file, "w") as f:
        f.write(contents)

    if silent:
        return

    print(f"Written file to drive:\n\tname: {output_filename}\n\tpath: {output_file_path}")
    return
