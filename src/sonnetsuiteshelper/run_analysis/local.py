import os
import subprocess


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

    print(cmd_output)

    return
