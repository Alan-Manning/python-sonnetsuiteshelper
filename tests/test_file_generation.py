import filecmp
import inspect
import os
import shutil

import pytest

from sonnetsuiteshelper import file_generation

"""
tests - file_generation.py.
    generate_file_like function testing.
        [X] - base file is not present
        [X] - output directory doesnt exist

        [X] - make file with no alterations
        [X] - no .son file extentions

        [X] - make file with 1 param changed
        [X] - make file with many params changed
        [X] - make file with params not in file changed

        [X] - make file with 1 general metal changed
        [X] - make file with many general metals changed
        [X] - make file with general metals not in file changed
        [X] - make file with many general metals with incorrect keys

        [X] - make file with many general metals and many params changed

        [X] - make file with adaptive sweep changed

        [X] - make file with linear sweep changed
"""

desired_output_files_path = r"tests/test_files/test_desired_output_files"
generated_output_file_path = r"tests/test_files/test_output_files"

base_filename_to_edit = r"general_base_file.son"
base_file_path_to_edit = r"tests/test_files/test_base_files"


def test_base_file_not_present() -> None:
    base_filename = "not_a_file.son"
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {}
    sweeps_to_edit = {}

    # check that is raises a FileNotFoundError
    with pytest.raises(FileNotFoundError):
        file_generation.generate_file_like(
            base_filename=base_filename,
            output_filename=output_filename,
            base_file_path=base_file_path,
            output_file_path=output_file_path,
            output_filename_prefix=output_filename_prefix,
            output_filename_suffix=output_filename_suffix,
            params_to_edit=params_to_edit,
            general_metals_to_edit=general_metals_to_edit,
            adaptive_sweeps_to_edit=sweeps_to_edit,
        )


def test_output_dir_doesnt_exist() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path + r"/new_folder_created"
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {}
    sweeps_to_edit = {}

    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    if os.path.isfile(generated_file):
        shutil.rmtree(output_file_path)

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__no_alterations() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {}
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__no_son_extentions() -> None:
    base_filename = base_filename_to_edit[:-4]
    output_filename = inspect.stack()[0][3] + ".son"  # current function name + ".son"
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {}
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename[:-4]}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__1_param_changed() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {"COUPLER": 222}
    general_metals_to_edit = {}
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__many_params_changed() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {
        "IDC_ARM_10": 1100,
        "IDC_ARM_11": 1100,
        "IDC_ARM_12": 1100,
        "IDC_ARM_13": 1100,
        "IDC_ARM_14": 1100,
        "IDC_ARM_15": 1100,
        "IDC_ARM_16": 1100,
        "IDC_ARM_17": 1100,
        "IDC_ARM_18": 1100,
        "IDC_ARM_19": 1100,
    }
    general_metals_to_edit = {}
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__params_not_in_file_changed() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {
        "NOT_A_VARIABLE": 1500,
        "TESTING": 100,
        "idc_arm_10": 1234,
    }
    general_metals_to_edit = {}
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__1_general_metal_changed() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {"Al": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8}}
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__many_general_metals_changed() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {
        "Al": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8},
        ".mets": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8},
        "Nb": {"Rdc": 1e-08, "Rrf": 1e-18, "Xdc": 0, "Ls": 0.003},
        "AL_alteredLK": {"Rdc": 0, "Rrf": 0, "Xdc": 0, "Ls": 10.3},
    }
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__many_general_metals_not_in_file() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {
        "Not a metal": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8},
        "still_not_a_metal": {"Rdc": 0, "Rrf": 0, "Xdc": 0, "Ls": 10.3},
    }
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__many_general_metals_with_incorrect_keys() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {
        "Al": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8},
        ".mets": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8},
        "Nb": {"RdWc": 1e-08, "Rrf": 1e-18, "Xdc": 0, "Ls": 0.003},
        "AL_alteredLK": {
            "Rdc": 0,
            "Rrf": 0,
            "Xdc": 0,
            "Ls": 10.3,
            "Another_irelevant_key": 1,
        },
    }
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__many_general_metals_and_many_params_changed() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {"COUPLER": 100, "IDC_ARM_20": 400}
    general_metals_to_edit = {
        "Al": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8},
        ".mets": {"Rdc": 0.5, "Rrf": 0.6, "Xdc": 0.7, "Ls": 0.8},
        "Nb": {"Rdc": 1e-08, "Rrf": 1e-18, "Xdc": 0, "Ls": 0.003},
        "AL_alteredLK": {"Rdc": 0, "Rrf": 0, "Xdc": 0, "Ls": 10.3},
    }
    sweeps_to_edit = {}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__adaptive_sweep_changed() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {}
    sweeps_to_edit = {"sweep_min": 8.5, "sweep_max": 10.5, "target_freqs": 500}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        adaptive_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output


def test_generate_file_like__linear_sweep_changed() -> None:
    base_filename = base_filename_to_edit
    output_filename = inspect.stack()[0][3]  # current function name
    base_file_path = base_file_path_to_edit
    output_file_path = generated_output_file_path
    output_filename_prefix = ""
    output_filename_suffix = ""
    params_to_edit = {}
    general_metals_to_edit = {}
    sweeps_to_edit = {"sweep_min": 0.2, "sweep_max": 15.3, "step_size": 0.01}

    file_generation.generate_file_like(
        base_filename=base_filename,
        output_filename=output_filename,
        base_file_path=base_file_path,
        output_file_path=output_file_path,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
        params_to_edit=params_to_edit,
        general_metals_to_edit=general_metals_to_edit,
        linear_sweeps_to_edit=sweeps_to_edit,
    )

    # compare the output to the desired output.
    generated_filename = f"{output_filename_prefix}{output_filename}{output_filename_suffix}.son"
    generated_file = os.path.join(output_file_path, generated_filename)

    desired_output_file = os.path.join(desired_output_files_path, f"{output_filename}.son")

    generated_file_matches_desired_output = filecmp.cmp(generated_file, desired_output_file)

    assert generated_file_matches_desired_output
