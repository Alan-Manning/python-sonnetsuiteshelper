import copy
import os

import numpy as np
import yaml
from matplotlib import pyplot as plt

from . import analysis_tools, file_generation


class SimpleSingleParamOptimiser:
    """Optimiser for Sonnet files.

    This takes in an initial .son file and .csv output from running
    that sonnet file and will try to optimise that file for a specific value
    within some defined tolerance.

    Attributes
    ----------
    name : str
        The unique name of this optimisation used for file generation. If
        this conflicts with another optimisers name then there will be
        files overwriting eachother.

    batch_1_son_filename : str
        The name of the first sonnet file which is the starting point for
        the optimiser. e.g. "son_sim_V1.son"

    batch_1_son_file_path : str
        The file path of the first sonnet file which is the starting point
        for the optimiser. e.g. if the folder structure looks like this:
        "batch_1_son_files/son_sim_V1.son", then the path is "batch_1_son_files".

    batch_1_output_filename : str
        The name of the first output file from a simulation which is the
        starting point for the optimiser. e.g. "son_sim_V1.csv". Often this is
        the same name as the initial son file.

    batch_1_output_file_path : str
        The file path of the first output file which is the starting point for
        the optimiser. e.g. if the folder structure looks like this:
        "batch_1_out/son_sim_V1.csv", then the path is "batch_1_out".
        Often this is the same path as the son file path.

    correlation : int
        The correlation between the variable parameter and the desired
        output param. This accepts str values "+" or "-".
        If an increase in the variable_param_value results in an increase in the
        desired_output_param, then this should be "+".
        If an increase in the variable_param_value results in a decrease in the
        desired_output_param, Then this should be "-".

    desired_output_param : str
        The variable output the optimiser should be optimising for. e.g.
        if trying to get a resonant frequency of 2GHz, then this argument
        will be ' desired_output_param="f0" '.
        This will only take values of:
        {"QR", "QC", "QI", "f0", "three_dB_BW"}.

    desired_output_param_value : str
        The value of the desired_output_param. e.g. if trying to
        resonant frequency of 2GHz, then this argument will be
        'desired_output_param_value=2.0e9'.

    desired_output_param_value_tolerence_percent : float
        This is the percentage tolerance around the desired_output_param_value.
        eg. if trying to get resonant frequency of 2GHz +- 1%, then this
        argument will be 'desired_output_param_value_tolerence_percent = 0.01'.

    desired_output_param_values : list
        This is a list of the desired ouptut parameter values from the optimser.

    sonnet_mesh_size : float
        Default=1.0. The mesh size in sonnet. This is the smallest change
        possible in the varaible parameter that will result in a different
        file being produced.

    next_variable_param_value : float
        This is a the next variable parameter value to be used in the optimser.

    variable_param_name : str
        The name of the parameter that should be varied by the optimiser
        to achieve the desired result.

    variable_param_values : list
        This is a list of the variable parameter values used in the optimser.
    """

    def __init__(
        self,
        unique_name: str,
        varaible_param_name: str,
        batch_1_son_filename: str,
        batch_1_son_file_path: str,
        batch_1_output_filename: str,
        batch_1_output_file_path: str,
        init_variable_param_value: float,
        desired_output_param: str,
        desired_output_param_value: float,
        desired_output_param_value_tolerence_percent: float,
        correlation: str,
        sonnet_mesh_size: float = 1.0,
    ):
        """
        Parameters
        ----------
        unique_name : str
            The unique name of this optimisation used for file generation. If
            this conflicts with another optimisers name then there will be
            files overwriting eachother.

        varaible_param_name: str
            The name of the parameter that should be varied by the optimiser
            to achieve the desired result.

        batch_1_son_filename: str
            The name of the first sonnet file which is the starting point for
            the optimiser. e.g. "son_sim_V1.son"

        batch_1_son_file_path: str
            The file path of the first sonnet file which is the starting point
            for the optimiser. e.g. if the folder structure looks like this:
            "batch_1_son_files/son_sim_V1.son", then the path is "batch_1_son_files".

        batch_1_output_filename: str
            The name of the first output file from a simulation which is the
            starting point for the optimiser. e.g. "son_sim_V1.csv".
            Often this is the same name as the initial son file.

        batch_1_output_file_path: str
            The file path of the first output file which is the starting point for
            the optimiser. e.g. if the folder structure looks like this:
            "batch_1_out/son_sim_V1.csv", then the path is "batch_1_out".
            Often this is the same path as the son file path.

        desired_output_param : str
            The variable output the optimiser should be optimising for. e.g.
            if trying to get a resonant frequency of 2GHz, then this argument
            will be ' desired_output_param="f0" '.
            This will only take values of:
            {"QR", "QC", "QI", "f0", "three_dB_BW"}.

        desired_output_param_value: float
            The value of the desired_output_param. e.g. if trying to
            resonant frequency of 2GHz, then this argument will be
            'desired_output_param_value=2.0e9'.

        desired_output_param_value_tolerence_percent: float
            This is the percentage tolerance around the desired_output_param_value.
            eg. if trying to get resonant frequency of 2GHz +- 1%, then this
            argument will be 'desired_output_param_value_tolerence_percent = 0.01'.

        correlation: str
            The correlation between the variable parameter and the desired
            output param. This accepts str values "+" or "-".
            If an increase in the variable_param_value results in an increase
            in the desired_output_param, then this should be "+".
            If an increase in the variable_param_value results in a decrease
            in the desired_output_param, Then this should be "-".

        sonnet_mesh_size : float or int
            Default=1.0. The mesh size in sonnet. This is the smallest change
            possible in the varaible parameter that will result in a different
            file being produced.

        note these values are ints because the grid mesh size in sonnet is 1um
        so cant analyze anything other than ints.
        """

        # Check corrent format of arguments
        acceptable_output_param_strings = ["QR", "QC", "QI", "f0", "three_dB_BW"]
        if desired_output_param not in acceptable_output_param_strings:
            raise ValueError(f"Cannot optimise for {desired_output_param}. Can only optimise for {acceptable_output_param_strings}")

        acceptable_correlation_strings = ["+", "-"]
        if correlation not in acceptable_correlation_strings:
            raise ValueError(f"Cannot correlate {correlation}. Can only use {acceptable_correlation_strings}")

        if batch_1_son_filename[-4:] != ".son":
            raise ValueError(f"batch_1_son_filename should be a sonnet file. This means it should contain a '.son' file extention.")

        if batch_1_output_filename[-4:] != ".csv":
            raise ValueError(
                f"batch_1_output_filename should be a csv output file from a simulation. This means it should contain a '.csv' file extention."
            )
        # General setup
        self.name = unique_name
        self.correlation = +1 if correlation == "+" else -1

        # Variable param setup
        self.variable_param_name = varaible_param_name
        self.variable_param_values = []

        # Desired param setup
        self.desired_output_param = desired_output_param
        self.desired_output_param_value = desired_output_param_value
        self.desired_output_param_value_tolerence_percent = desired_output_param_value_tolerence_percent
        self.desired_output_param_values = []

        # File settings
        self.sonnet_mesh_size = sonnet_mesh_size

        # Analyse first batch initial simulations
        self.batch_1_son_filename = batch_1_son_filename
        self.batch_1_son_file_path = batch_1_son_file_path

        self.batch_1_output_filename = batch_1_output_filename
        self.batch_1_output_file_path = batch_1_output_file_path

        self.next_variable_param_value = init_variable_param_value
        self.analyze_batch()
        self.generate_next_batch()

    def __str__(self) -> str:
        string = "Simple_single_param_optimiser"
        string += f"\n\t   current_batch_no: {self.get_current_batch_no()}"
        string += f"\n\tvariable_param_name: {self.variable_param_name}"
        string += f"\n\tdesired_output_param: {self.desired_output_param}"
        string += f"\n\tdesired_output_param_value: {self.desired_output_param_value}"
        return string

    def __getstate__(self) -> str:
        """Get the state of the object for pyyaml."""
        return dict(
            name=self.name,
            correlation=self.correlation,
            variable_param_name=self.variable_param_name,
            variable_param_values=self.variable_param_values,
            desired_output_param=self.desired_output_param,
            desired_output_param_value=self.desired_output_param_value,
            desired_output_param_value_tolerence_percent=self.desired_output_param_value_tolerence_percent,
            desired_output_param_values=self.desired_output_param_values,
            sonnet_mesh_size=self.sonnet_mesh_size,
            batch_1_son_filename=self.batch_1_son_filename,
            batch_1_son_file_path=self.batch_1_son_file_path,
            batch_1_output_filename=self.batch_1_output_filename,
            batch_1_output_file_path=self.batch_1_output_file_path,
        )

    def get_cache_filename_and_path(self) -> str:
        """Get the filename and file path for the optimiser cache file."""
        return os.path.join(self.get_cache_file_path(), self.get_cache_filename())

    def get_cache_file_path(self) -> str:
        """Get the file path for the optimiser cache file."""
        file_path = "OptCache"
        return file_path

    def get_cache_filename(self) -> str:
        """Get the filename for the optimiser cache file."""
        filename = f"SSPOC_{self.name}.yml"
        return filename

    def cache_results(self) -> None:
        """Cache the results of the optimiser so far into a yaml file.

        This results in the optimser not regernerating and reanalysing
        files.
        """
        # check output_directory exists and if not try to create it.
        if not os.path.isdir(self.get_cache_file_path()):
            try:
                os.mkdir(self.get_cache_file_path())
            except Exception as err:
                raise err

        with open(self.get_cache_filename_and_path(), "w+") as yaml_file:
            yaml.dump(self, yaml_file, default_flow_style=False)

        return

    def get_cached_results(self) -> None:
        """Get cached results of the optimiser so far if a cache file
        exists."""

        cache_file = self.get_cache_filename_and_path()
        if os.path.isfile(cache_file):
            try:
                cached_data = yaml.safe_load(cache_file)
                self.name = cached_data["name"]
                self.correlation = cached_data["correlation"]
                self.variable_param_name = cached_data["variable_param_name"]
                self.variable_param_values = cached_data["variable_param_values"]
                self.desired_output_param = cached_data["desired_output_param"]
                self.desired_output_param_value = cached_data["desired_output_param_value"]
                self.desired_output_param_value_tolerence_percent = cached_data["desired_output_param_value_tolerence_percent"]
                self.desired_output_param_values = cached_data["desired_output_param_values"]
                self.sonnet_mesh_size = cached_data["sonnet_mesh_size"]
                self.batch_1_son_filename = cached_data["batch_1_son_filename"]
                self.batch_1_son_file_path = cached_data["batch_1_son_file_path"]
                self.batch_1_output_filename = cached_data["batch_1_output_filename"]
                self.batch_1_output_file_path = cached_data["batch_1_output_file_path"]
            except Exception as e:
                print("Error loading cache")
                raise e

        return

    def get_current_batch_no(self) -> int:
        """Get the current batch number."""
        current_batch_no = len(self.variable_param_values)
        return current_batch_no

    def get_next_batch_no(self) -> int:
        """Get the current batch number."""
        next_batch_number = self.get_current_batch_no() + 1
        return next_batch_number

    def get_next_output_filename(self) -> str:
        """Get the output filename for the next batch's generated file."""
        output_filename = f"batch_{self.get_next_batch_no()}__{self.name}_{self.variable_param_name}_{self.next_variable_param_value}.son"
        return output_filename

    def get_next_output_file_path(self) -> str:
        """Get the output filepath for the next batch's generated file."""
        output_filepath = f"batch_{self.get_next_batch_no()}_generated_files"
        return output_filepath

    def get_last_analysis_filename(self) -> str:
        """Get the filename of the output file from the last batch that has
        been simulated in sonnet."""
        # Strip the .son file extention and add csv extention
        analysed_filename = self.get_next_output_filename()[:-4] + ".csv"
        return analysed_filename

    def get_last_analysis_file_path(self) -> str:
        """Get the file path of the output file from the last batch that has
        been simulated in sonnet."""
        analysed_file_path = f"batch_{self.get_next_batch_no()}_outputs"
        return analysed_file_path

    def get_optimised_filename(self) -> str:
        """Get the filename of the optimised file."""
        # Strip the .son file extention and add csv extention
        if self.last_result_reached_optimisation():
            optimised_filename = self.get_last_output_filename()[:-4] + ".csv"
            return optimised_filename
        else:
            raise (LookupError("Could not get optimised filename. Optimiser has not yet found optimised values."))

    def get_optimised_file_path(self) -> str:
        """Get the file path of the optimised file."""
        if self.last_result_reached_optimisation():
            optimised_file_path = f"batch_{self.get_current_batch_no()}_outputs"
            return optimised_file_path
        else:
            raise (LookupError("Could not get optimised file path. Optimiser has not yet found optimised values."))

    def get_last_output_filename(self) -> str:
        """Get the output filename for the last batch's generated file."""
        if self.get_current_batch_no() == 1:
            output_filename = self.batch_1_son_filename
        else:
            output_filename = (
                f"batch_{self.get_current_batch_no()}__{self.name}_{self.variable_param_name}_{self.variable_param_values[-1]}.son"
            )
        return output_filename

    def get_last_output_file_path(self) -> str:
        """Get the output filepath for the next batch's generated file."""
        if self.get_current_batch_no() == 1:
            output_filepath = self.batch_1_son_file_path
        else:
            output_filepath = f"batch_{self.get_current_batch_no()}_generated_files"
        return output_filepath

    def get_last_desired_output_param_value(self) -> float:
        """Get the last desired output param value from the last analysis."""
        return self.desired_output_param_values[-1]

    def get_last_variable_param_value(self) -> float:
        """Get the last variable param value from the last analysis."""
        return self.variable_param_values[-1]

    def append_new_results_to_self(self, output_value: float) -> None:
        """Append the analysed results to self."""
        self.desired_output_param_values.append(output_value)
        self.variable_param_values.append(self.next_variable_param_value)
        return

    def last_result_reached_optimisation(self) -> bool:
        """Check of the last desired_output_param_value is within the tolerance
        of the desired_output_param_value.

        If des*(1+tol) <= (last output vlaue) <= des*(1+tol) -> True
        else False.
        """
        last = self.get_last_desired_output_param_value()
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

    def round_to_sonnet_mesh_size(self, value) -> float:
        """Round the input value to the nearest sonnet_mesh_size step."""
        rounded_result = np.round(float(value) / self.sonnet_mesh_size) * self.sonnet_mesh_size
        return rounded_result

    def get_next_variable_param_value(self) -> float:
        """Generate the next varialbe param value for the next batch output
        file."""

        # If less than or 3 batches run then use a simple scale to generate next
        if self.get_current_batch_no() <= 3:
            next_variable_param_value = self.get_next_variable_param_value_from_percent_scale()
            return next_variable_param_value

        next_variable_param_value = self.get_next_variable_param_value_from_lin_fit()

        # If the next is the same as the last then try to percentage scale rather than lin fit.
        if next_variable_param_value == self.get_last_variable_param_value():
            next_variable_param_value = self.get_next_variable_param_value_from_percent_scale()
            # If the next value is still the same try to change the value by the sonnet_mesh_size.
            if next_variable_param_value == self.get_last_variable_param_value():
                next_variable_param_value = self.change_variable_param_value_by_mesh_step()

        return next_variable_param_value

    def change_variable_param_value_by_mesh_step(self) -> float:
        """Changes the curent variable_param_value by the sonnet file mesh
        size.

        This follows similar logic to the percent scale but only
        increases or decreases the value by the sonnet_mesh_size.
        """
        if self.get_last_desired_output_param_value() > self.desired_output_param_value:
            new_value = self.get_last_variable_param_value() + (self.correlation * self.sonnet_mesh_size)
        else:
            new_value = self.get_last_variable_param_value() - (self.correlation * self.sonnet_mesh_size)

        return new_value

    def get_next_variable_param_value_from_percent_scale(self) -> float:
        """Get the next variable value from simply adding/subtracting to the
        previous variable value by some adjust adjust strength multiplied by
        the delta between the last output value and the fnal desired output
        value. i.e. next = last +- (delta_from_desired*adjust_strength).

        This result is then rounded to the nearest sonnet mesh grid
        point.
        """
        delta_from_desired = abs(self.get_last_desired_output_param_value() - self.desired_output_param_value)
        adjust_strength = 0.002
        delta_in_variable_param = adjust_strength * delta_from_desired

        if self.get_last_desired_output_param_value() > self.desired_output_param_value:
            new_value = self.get_last_variable_param_value() - (self.correlation * delta_in_variable_param)
        else:
            new_value = self.get_last_variable_param_value() + (self.correlation * delta_in_variable_param)

        return self.round_to_sonnet_mesh_size(new_value)

    def get_next_variable_param_value_from_lin_fit(self) -> float:
        """Get the next variable value by lin fitting the data. This makes a
        linear fit and then gets the variable value that results in an
        intersection with the desired_output_param_value.

        This result is then rounded to the nearest sonnet mesh grid
        point.
        """
        x_data = np.array(self.variable_param_values)
        y_data = np.array(self.desired_output_param_values)
        poly_fit = np.polyfit(y_data, x_data, deg=1)
        poly_func = np.poly1d(poly_fit)
        new_value = poly_func(self.desired_output_param_value)

        return self.round_to_sonnet_mesh_size(new_value)

    def generate_next_batch(self, override_variable_param_value: float | None = None, ignore_automatic_stop: bool = False) -> None:
        """Generate the next batch of simulation files.

        Parameters
        ----------
        override_variable_param_value: float
            This is the value that will be used to generate the next batch
            file.

        ignore_automatic_stop: bool
            Default False. If True this will continue to generate the next
            batch even though it has reached the desired value.

        Outputs
        -------
        sonnet file: .son file
            This generates a .son file with the varable param changed.
            The file name for this file is :
            "{batch_no}_{name}__{varaible_param_name}_{variable_param_value}.son"
        """
        if self.last_result_reached_optimisation():
            print(f"Optimiser {self.name} Reached desired QR")
            print(f"\tBatch_number = {self.get_current_batch_no()}")
            print(f"\t{self.desired_output_param} = {self.get_last_desired_output_param_value()}")
            print(f"\t{self.variable_param_name} = {self.get_last_variable_param_value()}")

        if (not ignore_automatic_stop) and self.last_result_reached_optimisation():
            return

        if override_variable_param_value is None:
            variable_param_value = self.get_next_variable_param_value()
        else:
            variable_param_value = override_variable_param_value

        self.next_variable_param_value = variable_param_value

        name_for_output_file = self.get_next_output_filename()
        output_file_path = self.get_next_output_file_path()

        params_to_edit_dict = {self.variable_param_name: variable_param_value}

        last_filename = self.get_last_output_filename()
        last_file_path = self.get_last_output_file_path()

        file_generation.generate_file_like(
            base_filename=last_filename,
            base_file_path=last_file_path,
            output_filename=name_for_output_file,
            output_file_path=output_file_path,
            params_to_edit=params_to_edit_dict,
        )
        return

    def analyze_batch(self) -> None:
        """Analyze the current batch of simulations that have been run."""
        if self.get_current_batch_no() == 0:
            # special case for first batch
            son_csv = analysis_tools.SonnetCSVOutputFile(self.batch_1_output_filename, file_path=self.batch_1_output_file_path)
        else:
            filename = self.get_last_analysis_filename()
            file_path = self.get_last_analysis_file_path()

            son_csv = analysis_tools.SonnetCSVOutputFile(filename, file_path=file_path)

        f0 = son_csv.get_resonant_freq()
        QR, QC, QI = son_csv.get_Q_values()
        three_dB_BW = son_csv.get_three_dB_BW()

        match self.desired_output_param:
            case "QR":
                self.append_new_results_to_self(QR)
            case "QC":
                self.append_new_results_to_self(QC)
            case "QI":
                self.append_new_results_to_self(QI)
            case "f0":
                self.append_new_results_to_self(f0)
            case "three_dB_BW":
                self.append_new_results_to_self(three_dB_BW)
            case _:
                print("ERROR")
                raise (ValueError(f"Error, cannot optimise for {self.desired_output_param}"))

        self.cache_results()
        return

    def plot_optimisation(
        self,
        fig_ax: plt.Axes | None = None,
        plot_fit_function: bool = True,
        plot_next_batch_variable_value: bool = True,
        set_axis_labels: bool = True,
    ) -> None:
        """Plot the current results of the optimiser."""

        x_data = np.array(self.variable_param_values)
        x_label = self.variable_param_name

        y_data = np.array(self.desired_output_param_values)
        y_label = self.desired_output_param

        face_color_for_optimised = "#b4f7ab"
        face_color_for_not_optimised = "#fcc7bd"

        if fig_ax is None:
            title = f"{self.name} - {self.desired_output_param} vs {self.variable_param_name}"
            fig = plt.figure(title)
            rows = 1
            cols = 1
            grid = plt.GridSpec(rows, cols)
            ax = plt.subplot(grid[0, 0])
        else:
            ax = fig_ax

        phi = np.linspace(0, np.pi, len(x_data))
        rgb_cycle = (
            np.stack(
                (
                    np.cos(phi),
                    np.cos(phi + 2 * np.pi / 3),
                    np.cos(phi - 2 * np.pi / 3),
                )
            ).T
            + 1
        ) * 0.5

        for i, (x, y) in enumerate(zip(x_data, y_data)):
            ax.scatter(x, y, s=5, color=rgb_cycle[i])
            ax.annotate(f"{i+1}", (x, y))

        ax.axhline(y=self.desired_output_param_value)

        if plot_fit_function and self.get_current_batch_no() > 3:
            poly_fit = np.polyfit(x_data, y_data, deg=1)
            poly_func = np.poly1d(poly_fit)
            x_ax = np.linspace(min(x_data) * 0.999, max(x_data) * 1.001, 100)

            ax.plot(x_ax, poly_func(x_ax), label="fit")

        if plot_next_batch_variable_value and (not self.last_result_reached_optimisation()):
            next_variable_param_value = self.get_next_variable_param_value()
            ax.scatter(
                next_variable_param_value,
                self.desired_output_param_value,
                s=50,
                color="red",
                marker="x",
            )
            ax.annotate("N", (next_variable_param_value, self.desired_output_param_value))

        if self.last_result_reached_optimisation():
            ax.set_facecolor(face_color_for_optimised)
            ax.text(
                0.5,
                0.5,
                f"Finished at BATCH {self.get_current_batch_no()}",
                transform=ax.transAxes,
                color="gray",
                alpha=0.6,
                ha="center",
                va="center",
            )
        else:
            ax.set_facecolor(face_color_for_not_optimised)

        if set_axis_labels:
            ax.set_xlabel(f"{x_label}")
            ax.set_ylabel(f"{y_label}")

        if fig_ax is None:
            fig.show()

        return
