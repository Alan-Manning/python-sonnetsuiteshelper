import os
import subprocess
from typing import Dict


def analyze(project_name: str, remote: Dict = {}, param_file: str = ""):
    """
    Send a file to the emsolver for analysis. Can be sent locally or to a
    remote solver.

    Parameters
    ----------
    project_name : str
        This is the name of the sonnet file to be analyzed. If this does not
        include the .son file extention it will be added.

    KwArgs
    ------
    remote: Dict
        This is a dict that contains keys of host and port with respective
        values of the host name and the port number for the remote host.
        eg.
        >>> remote_solver = {
                "host" : "my_remote_solver",
                "port" : "51756"
            }

    param_file: str
        This is a parameter file name for a project. This should include the file
        extention and the path to that file.

    """

    emclient_path = r'"C:\Program Files\Sonnet Software\17.56\bin\emclient"'

    run_cmd = emclient_path

    # If this should be run remote try to add the remote to the run command
    if remote:
        keys_needed = ["host", "port"]
        if all(key in remote for key in keys_needed):
            run_cmd += f' -Server {remote["host"]}:{remote["port"]}'
        else:
            raise (
                KeyError(
                    f"remote parameter does not contain the keys needed.\nThe keys needed are {keys_needed}.\nCurrent keys are {list(remote.keys())}"
                )
            )

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
