import os
import re
from typing import Dict


def generate_file_like(
    base_filename: str,
    output_filename: str,
    base_file_path: str = "",
    output_file_path: str = "",
    output_filename_prefix: str = "",
    output_filename_suffix: str = "",
    params_to_edit: Dict = {},
    general_metals_to_edit: Dict = {},
    adaptive_sweeps_to_edit: Dict = {},
    linear_sweeps_to_edit: Dict = {},
) -> None:
    """This generates a Sonnet file like the base file specified. This will
    take in a series of values or other elements to further modify the Sonnet
    file to be produced.

    Parameters
    ----------
    base_filename : str
        This is the name of the base file, this will assume a ".son" file
        extention if this is not included in the base file name. This will be
        used to create the new Sonnet file. This can include the path of the
        file if it does not exist in the same directory as the python script.

    output_filename : str
        This is the name for the output file to be generated. If this does not
        have a ".son" file extention already, one will be added. If a file with
        this name already exists then its contents will be overwritten.

    KwArgs
    ------
    output_file_path : str
        This is the directory that the output file should be saved to.
        By default this is a blank string which will save the file in the same
        directory as the script. When specified the output file will be saved
        to this directory. If this directory does not already exist it will be
        created.

    output_filename_prefix : str
        This is a string to add to the beggining of the filename. Default is a
        blank string.

    output_filename_suffix : str
        This is a string to add to the end of the filename. Default is a
        blank string.

    params_to_edit : dict
        This is a dictionary that has keys of parameter names and values of the
        values those parameters should take. Note the values must be of type
        float or int. This can take any number of key and value pairs. If there
        is any parameter that isnt in the base file that exists in this dict
        then this will print an error and continue with the other parameter
        values. An example dict to be passed would take the form:
        >>> Params_to_edit = {
        ...     "Length_var_1" : 400,
        ...     "Length_var_2" : 250,
        ...     "Length_var_3" : 1975,
        ...     ...
        ... }

    general_metals_to_edit : dict
        This is a dictionary that has keys of general metal names and values of
        dictionarys with "Rdc", "Rrf", "Xdc", "Ls" key names and values with
        values for those keys. Note those keys must exist in the dict for each
        general metal to edit. Any number of general metals can be passed. If
        there is any metal in this dictionary that doesn't exist in the base
        file, or if that metal is there but has the wrong dict keys, this will
        print an error and continue with the other metals if there exist any.
        An example dict to be passed would take the form:
        >>> gen_mets_edits = {
        ...     "gen_met_1": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8},
        ...     "gen_met_2": {"Rdc": 1e-08, "Rrf": 14e-8, "Xdc": 0, "Ls": 0.003},
        ...     ...
        ... }

    adaptive_sweeps_to_edit : dict
        This is a dictionary that has keys of "sweep_min", "sweep_max",
        "target_freqs" and values of the values for those keys.
        An example dict to be passed would take the form:
        >>> adaptive_sweep = {
        ...     "sweep_min" : 1.0,
        ...     "sweep_max" : 5.0,
        ...     "target_freqs" : 500,
        ... }

    linear_sweeps_to_edit : dict
        This is a dictionary that has keys of "sweep_min", "sweep_max",
        "step_size" and values of the values for those keys.
        An example dict to be passed would take the form:
        >>> linear_sweep = {
        ...     "sweep_min" : 1.0,
        ...     "sweep_max" : 5.0,
        ...     "step_size" : 0.1,
        ... }

    Warnings
    --------
    If a file with this name already exists then its contents will be
    overwritten!
    """

    # if the basefile has no .son file extention add it.
    if base_filename[-4:] != ".son":
        base_filename = f"{base_filename}.son"

    # add the path for the basefile
    base_file = os.path.join(base_file_path, base_filename)

    # check base_file exists
    if not os.path.isfile(base_file):
        raise FileNotFoundError(f"Unable to find file: {base_file}")

    # check output_directory exists and if not try to create it.
    if not os.path.isdir(output_file_path):
        try:
            os.mkdir(output_file_path)
        except Exception as err:
            raise err

    # if .son file extention exists remove it. It is added next.
    if output_filename[-4:] == ".son":
        output_filename = output_filename[:-4]

    output_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"

    final_file = os.path.join(output_file_path, output_filename)

    with open(base_file) as f:
        contents = f.read()

    # If params dict not empty then change vals
    if params_to_edit:
        for key, val in params_to_edit.items():
            pattern = re.compile(rf'VALVAR {key} LNG (\w+|"\w+"|\d+\.\d+) "Dim\. Param\."')

            if pattern.search(contents):
                replacement = f'VALVAR {key} LNG {val} "Dim. Param."'
                contents = pattern.sub(replacement, contents)
            else:
                print(f"WARNING:\n\tParmeter {key} not found in file. Nothing changed, moving on.")

    # If general_metals dict not empty then change vals
    if general_metals_to_edit:
        keys_needed = ["Rdc", "Rrf", "Xdc", "Ls"]
        for metal_name, vals in general_metals_to_edit.items():
            # check that the correct keys are in the dict
            if not all(key in vals for key in keys_needed):
                print(
                    f'The "{metal_name}" general metal to edit does not have the correct keys. Keys needed are {keys_needed}. The keys present are {list(vals.keys())}.'
                )
                continue

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
                print(f"WARNING:\n\tGeneral metal {metal_name} not found in file. Nothing changed, moving on.")

    # If sweeps dict not empty then change vals
    if adaptive_sweeps_to_edit:
        keys_needed = ["sweep_min", "sweep_max", "target_freqs"]
        # check that the correct keys are in the dict and if so do replacement
        if all(key in adaptive_sweeps_to_edit for key in keys_needed):
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
                print("WARNING:\n\tCan't find an adaptive sweep to alter. Nothing changed, moving on.")

        else:
            print(
                f"The adaptive sweeps to edit does not have the correct keys. Keys needed are {keys_needed}. The keys present are {list(adaptive_sweeps_to_edit.keys())}."
            )

    # If sweeps dict not empty then change vals
    if linear_sweeps_to_edit:
        keys_needed = ["sweep_min", "sweep_max", "step_size"]
        # check that the correct keys are in the dict and if so do replacement
        if all(key in linear_sweeps_to_edit for key in keys_needed):
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
                print("WARNING:\n\tCan't find an linear sweep to alter. Nothing changed, moving on.")

        else:
            print(
                f"The linear sweeps to edit does not have the correct keys. Keys needed are {keys_needed}. The keys present are {list(linear_sweeps_to_edit.keys())}."
            )

    with open(final_file, "w") as f:
        f.write(contents)

    print(f"Written file to drive:\n\tname: {output_filename}\n\tpath: {output_file_path}")
    return
