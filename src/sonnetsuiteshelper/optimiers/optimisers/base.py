from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import yaml
from matplotlib.axes import Axes

from ...file_generation import generate_file_like
from ...utils.pretty_print import TextColor, pretty_print
from ..strategies import OptimiserStrategy
from .optimiser_settings import OptimiserSettings


@dataclass
class BatchFiles:
    batch_no: int
    filename: str
    son_file_path: str
    output_file_path: str


class FileManager:
    """File manager for the names and paths of files in a
    SingleParamOptimiser."""

    def __init__(
        self,
        batch_1_filename: str,
        batch_1_son_file_path: str,
        batch_1_output_file_path: str,
    ) -> None:
        """
        Parameters
        ----------
        batch_1_filename: str,
            The filename for the first batch. Do not include file extention.

        batch_1_son_file_path: str,
            The file path for where the first batch sonnet files are locatd.

        batch_1_output_file_path: str,
            The file path for where the first batch output files are locatd.
        """
        self.batch_to_files: dict[int, BatchFiles] = {}
        self.add(
            1,
            batch_1_filename,
            batch_1_son_file_path,
            batch_1_output_file_path,
        )

    def add(
        self,
        batch_no: int,
        filename: str,
        son_file_path: str,
        output_file_path: str,
    ) -> None:
        """Add a batch of filenames and paths to the file manager."""
        batch_files = BatchFiles(
            batch_no,
            filename,
            son_file_path,
            output_file_path,
        )
        self.batch_to_files[batch_no] = batch_files

    def get_batch_files(self, batch_no: int) -> BatchFiles:
        """Get the set of file names and paths for a given batch number."""
        batch_files = self.batch_to_files.get(batch_no)
        if batch_files is not None:
            return batch_files
        else:
            raise LookupError(f"Couldnt get batch_files for batch number {batch_no}.")

    def generate_filename(self, batch_no: int, name: str, variable_param_name: str, variable_param_value: float) -> str:
        """Generate a new filename from parms with the needed structure."""
        filename = f"batch_{batch_no}__{name}_{variable_param_name}_{variable_param_value}"
        return filename

    def get_filename(self, batch_no: int) -> str:
        """Get the filename for a given batch number."""
        batch_files = self.batch_to_files.get(batch_no)
        if batch_files is not None:
            return batch_files.filename
        else:
            raise LookupError(f"Couldnt get filename for batch number {batch_no}.")

    def get_sonnet_folder(self, batch_no: int) -> str:
        """Get the sonnet filepath.

        This is where son files are generated to.
        """
        batch_files = self.batch_to_files.get(batch_no)
        if batch_files is not None:
            return batch_files.son_file_path

        output_filepath = f"batch_{batch_no}_son_files"
        return output_filepath

    def get_output_folder(self, batch_no: int) -> str:
        """Get the output filepath.

        This is where outputs from son analysis are.
        """
        batch_files = self.batch_to_files.get(batch_no)
        if batch_files is not None:
            return batch_files.output_file_path

        output_filepath = f"batch_{batch_no}_outputs"
        return output_filepath


class SingleParamOptimiser(ABC):
    """SingleParamOptimiser."""

    ###########################################################################
    # abstract methods
    ###########################################################################
    @abstractmethod
    def _check_desired_output_param(self, desired_output_param: str) -> None:
        # should check if the desired_output_param is accepted
        pass

    @abstractmethod
    def _analyse_batch(
        self,
        filename: str,
        file_path: str,
        desired_output_param: str,
    ) -> float:
        pass

    @abstractmethod
    def plot(
        self,
        fig_ax: Axes | None = None,
        set_axis_labels: bool = True,
        plot_next_variable_param_value: bool = True,
        plot_strategy: bool = True,
    ) -> None:
        """Plot the current results of the optimiser.

        Parameters
        ----------
        fig_ax: Axes | None = None
            Default value `None` will generate a new figure. When specified
            this should be a figure axes of type `Axes` and the result will be
            ploted on this.

        set_axis_labels: bool = True,
            Default `True` will set the figure axes labels but will not when
            set to False.

        plot_next_variable_param_value: bool = True,
            Default `True` will plot the next value to be simulated to the
            figure axes labels but will not when set to False.

        plot_strategy: bool = True,
            Default `True` will attempt to plot the strategy that gives the
            next value to be simulated to the figure axes but will not when
            set to False.
        """
        pass

    ###########################################################################
    # concrete methods
    ###########################################################################

    def __init__(
        self,
        unique_name: str,
        batch_1_filename: str,
        batch_1_son_file_path: str,
        batch_1_output_file_path: str,
        init_variable_param_value: float,
        optimiser_settings: OptimiserSettings,
        ignore_loading_cache: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        unique_name : str
            The unique name of this optimisation used for file generation. If
            this conflicts with another optimisers name then there will be
            files overwriting eachother.

        batch_1_filename: str
            The name of the first sonnet file which is the starting point for
            the optimiser. e.g. "son_sim_V1". This shouldn't include the file
            extention.

        batch_1_son_file_path: str
            The file path of the first sonnet file which is the starting point
            for the optimiser. e.g. if the folder structure looks like this:
            "batch_1_son_files/son_sim_V1.son", then the path is
            "batch_1_son_files".

        batch_1_output_file_path: str
            The file path of the first output file which is the starting point
            for the optimiser. e.g. if the folder structure looks like this:
            "batch_1_out/son_sim_V1.csv", then the path is "batch_1_out".
            Often this is the same path as the son file path.

        optimiser_settings: OptimiserSettings
            This is an instace of an OptimiserSettings dataclass. This dictates
            how the optimiser works and what it is optimising for.

        ignore_loading_cache : bool
            Default=False. When True the optimser will not try to load cached
            results into memory. Otherwise by default the optimser will try to
            load values from a cache file in the OptCache path.

        """

        # Check corrent format of arguments
        self._check_desired_output_param(optimiser_settings.desired_output_param)

        accepted_correlation_strings = ["+", "-"]
        if optimiser_settings.correlation not in accepted_correlation_strings:
            raise ValueError(f"Cannot correlate with {optimiser_settings.correlation}. Can only use {accepted_correlation_strings}")

        if batch_1_filename[-4:] == ".son":
            raise ValueError(
                f"batch_1_filename `{batch_1_filename}` should just be a sonnet file name. This means it shouldn't contain a '.son' file extention."
            )

        # General setup
        self.name = unique_name

        if not isinstance(optimiser_settings.optimisation_strategy, OptimiserStrategy):
            raise TypeError(
                f"optimisation_strategy shoudl be of type `OptimiserStrategy`, not of type `{type(optimiser_settings.optimisation_strategy)}`."
            )
        self.optimisation_strategy = optimiser_settings.optimisation_strategy

        self.freq_unit: Literal["Hz", "KHz", "MHz", "GHz", "THz", "PHz"] = optimiser_settings.freq_unit
        self.number_of_ports: int = optimiser_settings.number_of_ports
        self.output_file_format: Literal["Spreadsheet"] = optimiser_settings.output_file_format

        self.cache_manager = CacheManager(self.name)

        # # Check for an existing cache file if ignore_loading_cache is False
        # if not ignore_loading_cache:
        #     self.load_cached_results()
        # else:
        #     self.loaded_cache = False
        #
        # if self.loaded_cache:
        #     return

        self.correlation: Literal[+1, -1] = +1 if optimiser_settings.correlation == "+" else -1

        if optimiser_settings.min_value_for_variable_param is None:
            self.min_value_for_variable_param = None
        elif isinstance(optimiser_settings.min_value_for_variable_param, float):
            self.min_value_for_variable_param = optimiser_settings.min_value_for_variable_param
        elif isinstance(optimiser_settings.min_value_for_variable_param, int):
            self.min_value_for_variable_param = float(optimiser_settings.min_value_for_variable_param)
        else:
            raise TypeError(
                f"min_value_for_variable_param should be of type `float` or None. Not of type `{type(optimiser_settings.min_value_for_variable_param)}`"
            )

        if optimiser_settings.max_value_for_variable_param is None:
            self.max_value_for_variable_param = None
        elif isinstance(optimiser_settings.max_value_for_variable_param, float):
            self.max_value_for_variable_param = optimiser_settings.max_value_for_variable_param
        elif isinstance(optimiser_settings.max_value_for_variable_param, int):
            self.max_value_for_variable_param = float(optimiser_settings.max_value_for_variable_param)
        else:
            raise TypeError(
                f"max_value_for_variable_param should be of type `float` or None. Not of type `{type(optimiser_settings.min_value_for_variable_param)}`"
            )

        # Variable param setup
        self.variable_param_name: str = optimiser_settings.varaible_param_name
        self.variable_param_values: list[float] = []

        # Desired param setup
        self.desired_output_param: str = optimiser_settings.desired_output_param
        self.desired_output_param_value: float = optimiser_settings.desired_output_param_value
        self.desired_output_param_value_tolerence_percent: float = optimiser_settings.desired_output_param_value_tolerence_percent
        self.desired_output_param_values: list[float] = []

        # File settings
        self.sonnet_mesh_size: float = optimiser_settings.sonnet_mesh_size

        # Analyse first batch initial simulations

        self.batch_1_filename: str = batch_1_filename
        self.batch_1_son_file_path: str = batch_1_son_file_path
        self.batch_1_output_file_path: str = batch_1_output_file_path

        self.file_manager = FileManager(
            batch_1_filename,
            batch_1_son_file_path,
            batch_1_output_file_path,
        )

        self.next_variable_param_value: float = init_variable_param_value

        self.analyse_batch()
        self.generate_next_batch()

    ###########################################################################

    def __str__(self) -> str:
        string = f"Optimiser: {self.name}"
        string += f"\n     optimisation_strategy: {self.optimisation_strategy.name}"
        string += f"\n          current_batch_no: {self.current_batch_no}"
        string += f"\n       variable_param_name: {self.variable_param_name}"
        string += f"\n      desired_output_param: {self.desired_output_param}"
        string += f"\ndesired_output_param_value: {self.desired_output_param_value}"
        return string

    ###########################################################################
    # Caching
    ###########################################################################
    def cache_results(self) -> None:
        """Cache the results of the optimiser so far into a yaml file.

        This results in the optimser not regernerating and reanalysing
        files.
        """
        return
        self.cache_manager.cache_results(
            self.variable_param_values,
            self.desired_output_param_values,
            self.file_manager,
        )
        return

    def loaded_cache(self) -> None:
        """Load cached results of the optimiser so far if a cache file
        exists."""
        self.cache_manager.load_cached_results(self)
        return

    ###########################################################################
    # batch management
    ###########################################################################
    @property
    def previus_batch_no(self) -> int:
        """Get the previus batch number."""
        return len(self.variable_param_values)

    @property
    def current_batch_no(self) -> int:
        """Get the current batch number."""
        return len(self.variable_param_values) + 1

    @property
    def next_batch_no(self) -> int:
        """Get the next batch number."""
        return self.current_batch_no + 1

    @property
    def current_desired_output_param_value(self) -> float:
        """Get the current desired output param value from the last
        analysis."""
        return self.desired_output_param_values[-1]

    @property
    def current_variable_param_value(self) -> float:
        """Get the current variable param value from the last analysis."""
        return self.variable_param_values[-1]

    ###########################################################################
    # value management
    ###########################################################################

    def append_new_results(self, analysed_value: float) -> None:
        """Append the analysed results to self."""
        self.desired_output_param_values.append(analysed_value)
        self.variable_param_values.append(self.next_variable_param_value)
        return

    ###########################################################################
    # optimised management
    ###########################################################################
    def has_reached_optimisation(self) -> bool:
        """Check of the last desired_output_param_value is within the tolerance
        of the desired_output_param_value.

        If des*(1-tol) <= (last output vlaue) <= des*(1+tol) -> True
        else False.
        """
        last = self.current_desired_output_param_value
        des = self.desired_output_param_value
        tol = self.desired_output_param_value_tolerence_percent

        outside = False
        if last <= des * (1 - tol):
            outside = True

        if last >= des * (1 + tol):
            outside = True

        if outside:
            return False
        else:
            return True

    @property
    def optimised_filename(self) -> str:
        """Get the filename of the optimised file."""
        if self.has_reached_optimisation():
            return self.file_manager.get_batch_files(self.current_batch_no).filename
        else:
            raise LookupError("Could not get optimised filename. Optimiser has not yet found an optimised value.")

    @property
    def optimised_sonnet_file_path(self) -> str:
        """Get the sonnet file path of the optimised sonnet file."""
        if self.has_reached_optimisation():
            return self.file_manager.get_batch_files(self.current_batch_no).son_file_path
        else:
            raise LookupError("Could not get optimised file path. Optimiser has not yet found an optimised value.")

    @property
    def optimised_output_file_path(self) -> str:
        """Get the output file path of the optimised file."""
        if self.has_reached_optimisation():
            return self.file_manager.get_batch_files(self.current_batch_no).output_file_path
        else:
            raise LookupError("Could not get optimised file path. Optimiser has not yet found an optimised value.")

    @property
    def optimised_variable_param_value(self) -> float:
        """Get the variable_param_value of the optimised file."""
        if self.has_reached_optimisation():
            return self.current_variable_param_value
        else:
            raise LookupError("Could not get optimised variable_param_value. Optimiser has not yet found an optimised value.")

    def _get_closest_to_optimised(self) -> tuple[int, float]:
        """Get the closest to optimised batch number and variable_param_value.
        This will return the values even if the values are considered
        optimised.

        Returns
        -------
        batch_no: int
            The batch number of the closest to optimised file.

        closest_variable_param_value: int
            The variable_param_value of the closest to optimised file.
        """
        abs_diff = np.abs(np.array(self.desired_output_param_values) - self.desired_output_param_value)
        arg_min = int(np.argmin(abs_diff))
        closest_variable_param_value = self.variable_param_values[arg_min]
        batch_no = arg_min + 1

        return batch_no, closest_variable_param_value

    def get_closest_to_optimised_variable_param_value(self) -> float:
        """Get the variable_param_value of the file that is currently the
        closest to having an optimised value.

        If an optimised file exists this will return that file, this is
        equivilant to self.optimised_variable_param_value().
        """
        try:
            optimised_variable_param_value = self.optimised_variable_param_value
            return optimised_variable_param_value
        except LookupError:
            # There isnt an optimised file so get the closest.
            _, closest_variable_param_value = self._get_closest_to_optimised()

            return closest_variable_param_value

    def get_closest_to_optimised_filename(self) -> str:
        """Get the filename of the file that is currently the closest to having
        an optimised value.

        If an optimised file exists this will return that file, this is
        equivilant to self.optimised_filename().
        """
        try:
            optimised_filename = self.optimised_filename
            return optimised_filename
        except LookupError:
            # There isnt an optimised file so get the closest.
            batch_no, closest_variable_param_value = self._get_closest_to_optimised()
            closest_filename = f"{self.file_manager.get_batch_files(batch_no).filename}.csv"

            return closest_filename

    def get_closest_to_optimised_sonnet_file_path(self) -> str:
        """Get the file path of the sonnet file that is currently the closest
        to having an optimised value."""
        try:
            optimised_file_path = self.optimised_sonnet_file_path
            return optimised_file_path
        except LookupError:
            # There isnt an optimised file so get the closest.
            batch_no, _ = self._get_closest_to_optimised()

            closest_optimised_file_path = self.file_manager.get_sonnet_folder(batch_no)
            return closest_optimised_file_path

    def get_closest_to_optimised_output_file_path(self) -> str:
        """Get the file path of the output file that is currently the closest
        to having an optimised value."""
        try:
            optimised_file_path = self.optimised_output_file_path
            return optimised_file_path
        except LookupError:
            # There isnt an optimised file so get the closest.
            batch_no, _ = self._get_closest_to_optimised()
            closest_optimised_file_path = self.file_manager.get_output_folder(batch_no)
            return closest_optimised_file_path

    ###########################################################################
    # generate files
    ###########################################################################

    def get_next_variable_param_value(self) -> float:
        next_value = self.optimisation_strategy.get_next_variable_param_value(
            self.current_desired_output_param_value,
            self.desired_output_param_value,
            self.variable_param_values,
            self.desired_output_param_values,
            self.correlation,
            self.sonnet_mesh_size,
        )

        if self.min_value_for_variable_param:
            if next_value < self.min_value_for_variable_param:
                pretty_print(f"\tGot variable_param_value `{next_value}` from {self.optimisation_strategy.name}.", color=TextColor.WARNING)
                pretty_print(f"\tThis exceeds the min allowed value of `{self.min_value_for_variable_param}`", color=TextColor.WARNING)
                pretty_print(f"\tThe value has been clamped to {self.min_value_for_variable_param}.", color=TextColor.WARNING)
                next_value = self.min_value_for_variable_param

        if self.max_value_for_variable_param:
            if next_value > self.max_value_for_variable_param:
                pretty_print(f"\tGot variable_param_value `{next_value}` from {self.optimisation_strategy.name}.", color=TextColor.WARNING)
                pretty_print(f"\tThis exceeds the max allowed value of `{self.min_value_for_variable_param}`", color=TextColor.WARNING)
                pretty_print(f"\tThe value has been clamped to {self.min_value_for_variable_param}.", color=TextColor.WARNING)
                next_value = self.max_value_for_variable_param

        return next_value

    def generate_next_batch(
        self,
        override_next: dict[int, float] | None = None,
        ignore_automatic_stop: dict[int, bool] | None = None,
        override_optimisation_strategy: dict[int, OptimiserStrategy] | None = None,
    ) -> None:
        """Generate the next batch of simulation files.

        Parameters
        ----------
        override_next: dict[int, float] | None = None
            Defaults to None. When defined this should be a dict with keys of
            the batch numbers and values of the override values. e.g.
            >>> override_next = {
            ...     2: 580,
            ...     5: 600,
            ...     6: 610,
            ... }

        ignore_automatic_stop: dict[int, bool]
            Defaults to None. When defined this should be a dict with keys of
            the batch numbers and values of the ignore_auto_stop values. e.g.
            >>> ignore_automatic_stop = {
            ...     7: True,
            ...     8: True,
            ...     9: True,
            ... }

        override_optimisation_strategy: dict[int, OptimiserStrategy]
            Defaults to None. When defined this should be a dict with keys of
            the next batch number and values of the optimser strategies. see example
            below. *Note* This is update the optimser strategy going forward so
            the batch no represents the point at which the switch to the new
            strategy happens.
            >>> strat_override = {
            ...     10: optimiers.strategies.LinFit(),
            ...     12: optimiers.strategies.PolyFit(2),
            ... }

        Outputs
        -------
        sonnet file: .son file
            This generates a .son file with the varable param changed.
            The file name for this file is given by self.next_filename
        """
        if self.has_reached_optimisation():
            pretty_print(f"Optimiser {self.name} Reached desired {self.desired_output_param}.", color=TextColor.GREEN)
            pretty_print(f"\tBatch_number = {self.current_batch_no - 1}", color=TextColor.GREEN)
            pretty_print(f"\t{self.desired_output_param} = {self.current_desired_output_param_value}", color=TextColor.GREEN)
            pretty_print(f"\t{self.variable_param_name} = {self.current_variable_param_value}", color=TextColor.GREEN)
            if ignore_automatic_stop is not None:
                if self.next_batch_no not in ignore_automatic_stop.keys():
                    self.cache_results()
                    return
                else:
                    print(f"Optimiser {self.name} got ignore automatic stop override for batch {self.next_batch_no}. Continuing.")
            else:
                self.cache_results()
                return

        variable_param_value = None

        # checking for override strategy
        if override_optimisation_strategy is not None:
            if self.current_batch_no in override_optimisation_strategy.keys():
                self.optimisation_strategy = override_optimisation_strategy[self.current_batch_no]
                pretty_print(f"\tSTRATEGY OVERRIDE FOR {self.name} FROM BATCH {self.current_batch_no}", color=TextColor.WARNING)

        # checking for override value
        if override_next is not None:
            if self.current_batch_no in override_next.keys():
                variable_param_value = override_next[self.current_batch_no]
                pretty_print(
                    f"\tOVERRIDE {self.name}: Batch {self.current_batch_no} - VALUE={variable_param_value}", color=TextColor.WARNING
                )

        # if no override get next normally
        if variable_param_value is None:
            variable_param_value = self.get_next_variable_param_value()

        self.next_variable_param_value = variable_param_value

        new_filename = self.file_manager.generate_filename(
            self.current_batch_no,
            self.name,
            self.variable_param_name,
            self.next_variable_param_value,
        )
        new_son_filename = new_filename
        new_son_file_path = self.file_manager.get_sonnet_folder(self.current_batch_no)
        new_output_file_path = self.file_manager.get_output_folder(self.current_batch_no)

        params_to_edit_dict = {self.variable_param_name: variable_param_value}

        current_file_batch = self.file_manager.get_batch_files(self.previus_batch_no)

        generate_file_like(
            base_filename=f"{current_file_batch.filename}.son",
            base_file_path=current_file_batch.son_file_path,
            output_filename=f"{new_son_filename}.son",
            output_file_path=new_son_file_path,
            params_to_edit=params_to_edit_dict,
            silent=True,
        )
        pretty_print(f"\tMade Batch:{self.current_batch_no} - VALUE={variable_param_value}", color=TextColor.CYAN)
        self.file_manager.add(
            self.current_batch_no,
            new_filename,
            new_son_file_path,
            new_output_file_path,
        )

        self.cache_results()
        return

    ###########################################################################
    # Analyse files
    ###########################################################################
    def analyse_batch(self) -> None:
        """Analyse the current batch of simulations that have been run."""
        # breakpoint()
        batch_files = self.file_manager.get_batch_files(self.current_batch_no)
        # print()
        # print(self.file_manager.batch_to_files)
        # print()
        if batch_files is None:
            raise RuntimeError(f"Batch does not exist: batch:{self.current_batch_no}")

        analysed_value = self._analyse_batch(batch_files.filename, batch_files.output_file_path, self.desired_output_param)
        if not isinstance(analysed_value, float):
            raise ValueError(
                f"analyse_batch got an unexpected return type of {type(analysed_value)}. This should have been of type float. Cannot continue with optimiser."
            )

        self.append_new_results(analysed_value)
        self.cache_results()


class CacheManager:
    """Cache manager for saving the state of the optimiser to a file.

    This cuts down of analysing/generating files that have already been
    analysed/generated
    """

    def __init__(self, name: str) -> None:
        """Cache Manager for saving optimiser state.

        Parameters
        ----------
        name: str
            The name of the optimiser.
        """
        self.name = name
        self.loaded_cache = False

        return

    @property
    def cache_file(self) -> Path:
        """The cache file Path object.

        filename and file path for the optimiser cache file.
        """
        cache_file_path = "OptCache"
        cache_filename = f"OPT_{self.name}.yml"
        cache_file = Path(cache_file_path, cache_filename)

        # create the output directory, if exists ignorre warning.
        cache_file.mkdir(exist_ok=True, parents=True)

        return cache_file

    def cache_results(
        self,
        variable_param_values: list[float],
        desired_output_param_values: list[float],
        file_manager: FileManager,
    ) -> None:
        """Cache the results of the optimiser so far into a yaml file.

        Parameters
        ----------

        variable_param_values: list[float],
            The optimiser's variable_param_values.

        desired_output_param_values: list[float],
            The optimiser's desired_output_param_values.
        """
        cache_file = self.cache_file

        # Making the yaml file string.
        state_str = "---\n"

        state_str = state_str + f"name: '{self.name}'\n"
        state_str = state_str + f"variable_param_values: {variable_param_values}\n"
        state_str = state_str + f"desired_output_param_values: {desired_output_param_values}\n"

        # Building the files section
        state_str = state_str + "files_data:\n"
        for batch_no, batch_files in file_manager.batch_to_files.items():
            state_str += f"\tbatch_{batch_no}:\n"
            state_str += f"\t\t:{batch_files.batch_no}\n"
            state_str += f"\t\t:{batch_files.filename}\n"
            state_str += f"\t\t:{batch_files.son_file_path}\n"
            state_str += f"\t\t:{batch_files.output_file_path}\n"

        with open(cache_file, "w+") as yaml_file:
            yaml_file.write(state_str)

        return

    def load_cached_results(self, optimiser: SingleParamOptimiser) -> None:
        """Load cached results of the optimiser so far if a cache file
        exists."""

        cache_file = self.cache_file

        if not cache_file.is_file():
            self.loaded_cache = False
            raise FileNotFoundError(f"Unable to find cache file: `{cache_file}`.")

        try:
            with open(cache_file, "r") as stream:
                cached_data = yaml.safe_load(stream)

            optimiser.variable_param_values = cached_data.get("variable_param_values")
            optimiser.desired_output_param_values = cached_data.get("desired_output_param_values")

            file_data = cached_data.get("file_data")
            # for key, val in file_data

        except Exception as e:
            print(f"Error loading cache. Cache file: `{cache_file}`.")
            raise e

        return
