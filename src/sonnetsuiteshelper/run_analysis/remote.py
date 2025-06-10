import os
import subprocess


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
