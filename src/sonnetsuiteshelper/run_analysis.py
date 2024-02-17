import os
import subprocess
from os.path import isfile
from sys import stdout
from typing import Dict


def analyze_local(
    project_name: str,
    sonnet_install_loc: str,
    display_analysis_info_live: bool = False,
    lossles: bool = False,
    abs_cache_none: bool = False,
    abs_cache_stop_restart: bool = False,
    abs_cache_multi_sweep: bool = False,
    abs_no_discrete: bool = False,
    sub_freq_Hz: int | None = None,
    param_file: str = "",
):
    """Send a file to the local Sonnet Suites Solver.

    Parameters
    ----------
    project_name : str
        The name of the sonnet file to be analyzed. If this does not include
        the ".son" file extention then it will be added.

    sonnet_install_loc : str
        This the directory of the sonnet install. This is needed to know the
        location of the em executable to be able to run the analysis.
        This is usually for windows:
        >>> C:/Program Files/Sonnet Software/XX.XX
        where 'XX.XX' is the version number, e.g. ".../Sonnet Software/17.56".

    display_analysis_info_live: bool
        Whether to display live analysis info in the terminal.

    lossles : bool
        Default False

    abs_cache_none : bool
        Default False,

    abs_cache_stop_restart: bool = False,
        Default False

    abs_cache_multi_sweep: bool = False,
        Default False

    abs_no_discrete: bool = False,
        Default False

    sub_freq_Hz: int | None = None,
        Default None

    param_file: str = "",
        Default is blank str

    See Also
    --------
    analyze_remote : remote server analysis.


    Referencees
    -----------
    .. _Sonnet User's Guide:
        https://www.sonnetsoftware.com/support/help-18/users_guide/Sonnet%20User's%20Guide.html?EmCommandLineforBatch.html
    """

    em_exec = os.path.join(sonnet_install_loc, r"bin\em")

    # Check the em executable exists for the provided sonnet install loc.
    if not os.path.isfile(em_exec):
        raise FileNotFoundError("Could not find em executable in sonnet install path.")

    # Check if the project name ends .son if not add it.
    if project_name[:-4] != ".son":
        project_name += ".son"

    # Check the project file exists.
    if not os.path.isfile(project_name):
        raise (FileNotFoundError)

    run_cmd = f"{em_exec} {project_name}"

    if display_analysis_info_live:
        run_cmd += " -v"

    if lossles:
        run_cmd += " -Lossles"

    if abs_cache_none:
        run_cmd += " -AbsCacheNone"

    if abs_cache_stop_restart:
        run_cmd += " -AbsCacheStopRestart"

    if abs_cache_multi_sweep:
        run_cmd += " -AbsCacheMultiSweep"

    if abs_no_discrete:
        run_cmd += " -AbsNoDiscrete"

    if sub_freq_Hz:
        run_cmd += f" -SubFreqHz[{sub_freq_Hz}]"

    if param_file:
        run_cmd += f" -ParamFile {param_file}"

    cmd_output = subprocess.Popen(run_cmd, shell=True, stdout=subprocess.PIPE.stdout.read())

    return


def analyze_remote(project_name: str, remote_host: str, remote_port: str, param_file: str = ""):
    """Send a file to a remote emsolver server for analysis.

    Parameters
    ----------
    project_name : str
        This is the name of the sonnet file to be analyzed. If this does not
        include the .son file extention it will be added.

    remote_host : str
        This is the host name for the remote solver. e.g. "10.1.10.30"

    remote_port : str
        This is the port to be used to connect to the remote solver. e.g. "56150"

    KwArgs
    ------
    param_file: str
        This is a parameter file name for a project. This should include the
        path for the file and the file extention.
    """
    run_cmd = ""

    # get emclient_path in argument
    emclient_path = r'"C:\Program Files\Sonnet Software\17.56\bin\emclient"'

    shell = "TODO"

    if shell == "ps":
        run_cmd += "& "

    run_cmd = emclient_path

    # If this should be run remote try to add the remote to the run command
    # remote = True
    # if remote:
    #     keys_needed = ["host", "port"]
    #     if all(key in remote for key in keys_needed):
    #         run_cmd += f' -Server {remote["host"]}:{remote["port"]}'
    #     else:
    #         raise (
    #             KeyError(
    #                 f"remote parameter does not contain the keys needed.\nThe keys needed are {keys_needed}.\nCurrent keys are {list(remote.keys())}"
    #             )
    #         )

    run_cmd += f" -ProjectName {project_name}"

    # If this should be run with a parameter file try to add it to the run command
    if param_file:
        if os.path.isfile(param_file):
            run_cmd += f" -ParamFile {param_file}"
        else:
            raise FileNotFoundError("Could not find the parameter file in given directory")

    run_cmd += r" -Analyze"

    # run the command that has been built up and capture output
    cmd_output = subprocess.Popen(run_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()

    return cmd_output
