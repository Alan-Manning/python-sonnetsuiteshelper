from collections.abc import Sequence
from os import get_terminal_size
from typing import Self

from ...utils.pretty_print import TextColor, TextStyle, pretty_print
from ..optimisers.base import SingleParamOptimiser
from ..strategies import OptimiserStrategy


class SingleParamOptimiserSet:
    """SingleParamOptimiserSet."""

    def __init__(self) -> None:
        self.optimisers: dict[str, SingleParamOptimiser] = {}
        self._index = 0

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> SingleParamOptimiser:
        if self._index < len(self.optimisers.keys()):
            current_key = list(self.optimisers.keys())[self._index]
            item = self.optimisers[current_key]
            self._index += 1
            return item
        else:
            self._index = 0
            raise StopIteration

    def __str__(self) -> str:
        string = "SingleParamOptimiserSet"
        string += "\nOptimisers in Set:"
        opt_names = list(self.optimisers.keys())
        for opt_name in opt_names:
            string += f"\n\t'{opt_name}'"
        return string

    def add(self, optimser: SingleParamOptimiser | Sequence[SingleParamOptimiser]):
        """Add a SingleParamOptimiser or a Sequence of SingleParamOptimiser's
        to the this set.

        Parameters
        ----------
        optimser: SingleParamOptimiser | Sequence[SingleParamOptimiser]
            A SingleParamOptimiser or a Sequence of SingleParamOptimiser's
        """
        # add single optimiser
        if not isinstance(optimser, Sequence):
            if optimser.name in self.optimisers.keys():
                raise KeyError(
                    f"An optimser with the name '{optimser.name}' already exists in the set of optimisers.\nUnable to add this to the set."
                )
            self.optimisers.update({optimser.name: optimser})
            return

        # add multiple optimisers
        for opt in optimser:
            if opt.name in self.optimisers.keys():
                raise KeyError(
                    f"An optimser with the name '{opt.name}' already exists in the set of optimisers.\nUnable to add this to the set."
                )
            self.optimisers.update({opt.name: opt})
        return

    def iter_batches(
        self,
        override_nexts: dict[str, dict[int, float]] | None = None,
        ignore_automatic_stops: dict[str, dict[int, bool]] | None = None,
        override_optimisation_strategies: dict[str, dict[int, OptimiserStrategy]] | None = None,
    ):
        """Try to analyse results and generate next batch for each optimser in
        set. This takes an override_variable_param_values dict which will
        override the variable_param_value from the SimpleSingleParamOptimiser.
        This also takes an ignore_automatic_stops dict which will override the
        automatic stop from the SimpleSingleParamOptimiser. See
        SimpleSingleParamOptimiser.generate_next_batch() for mroe details on
        these arguments.

        KwArgs
        ----------
        override_nexts: dict[str, dict[int, float]]
            Defaults to None. When defined this should be a dict with keys of
            the optimser names. The values for these will be a dict with
            batch number keys and the param_value values. e.g.
            >>> override_nexts = {
            ...     "optimser_name_1": {
            ...         2: 580,
            ...         5: 600,
            ...         6: 610,
            ...     },
            ...     "optimser_name_2": {
            ...         15: 600,
            ...     },
            ...     ...
            ... }

        ignore_automatic_stops: dict[str, dict[int, bool]]
            Defaults to None. When defined this should be a dict with keys of
            the optimser names. The values for these will be a dict with
            batch number keys and the ignore_auto_stop values. e.g.
            >>> ignore_automatic_stops = {
            ...     "optimser_name_1": {
            ...         7: True,
            ...         8: True,
            ...         9: True,
            ...     },
            ...     "optimser_name_2": {
            ...         15: True,
            ...     },
            ...     ...
            ... }

        override_optimisation_strategies: dict[str, dict[int, OptimiserStrategy]]
            Defaults to None. When defined this should be a dict with keys of
            the optimser names. The values for these will be a dict with
            batch number keys and the optimser strategies as values. see
            example below. *Note* This is update the optimser strategy going
            forward so the batch no represents the point at which the switch
            to the new strategy happens.
            >>> strat_overrides = {
            ...     "optimser_name_1": {
            ...         10: optimiers.strategies.LinFit(),
            ...     },
            ...     "optimser_name_2": {
            ...         12: optimiers.strategies.PolyFit(2),
            ...     },
            ...     ...
            ... }
        """
        # check all the keys in override_nexts to make sure the optimiser exists.
        if override_nexts is not None:
            for key in override_nexts.keys():
                if key not in self.optimisers.keys():
                    raise KeyError(f"override_nexts has key `{key}` which doesn't corrospond to any optimiser in this optimiser set.")

        # check all the keys in ignore_automatic_stops to make sure the optimiser exists.
        if ignore_automatic_stops is not None:
            for key in ignore_automatic_stops.keys():
                if key not in self.optimisers.keys():
                    raise KeyError(
                        f"ignore_automatic_stops has key `{key}` which doesn't corrospond to any optimiser in this optimiser set."
                    )

        # check all the keys in override_optimisation_strategies to make sure the optimiser exists.
        if override_optimisation_strategies is not None:
            for key in override_optimisation_strategies.keys():
                if key not in self.optimisers.keys():
                    raise KeyError(
                        f"override_optimisation_strategies has key `{key}` which doesn't corrospond to any optimiser in this optimiser set."
                    )

        stop_iter_batch_dict: dict[str, bool] = {}
        for opt_name in self.optimisers.keys():
            stop_iter_batch_dict[opt_name] = False

        count = 2
        term_width = get_terminal_size().columns
        while not all(stop_iter_batch_dict.values()):
            pretty_print(
                "#" * term_width,
                color=[TextColor.WHITE, TextColor.BLUE_BG],
                style=TextStyle.BOLD,
            )
            pretty_print(
                "#" + f"Batch {count}".center(term_width - 2) + "#",
                color=[TextColor.WHITE, TextColor.BLUE_BG],
                style=TextStyle.BOLD,
            )
            count += 1
            pretty_print(
                "#" * term_width,
                color=[TextColor.WHITE, TextColor.BLUE_BG],
                style=TextStyle.BOLD,
            )
            for opt_name, optimiser in self.optimisers.items():
                print(f"{opt_name}: Batch {optimiser.current_batch_no}.")

                override_next = override_nexts.get(optimiser.name, None) if override_nexts else None
                ignore_automatic_stop = ignore_automatic_stops.get(optimiser.name, None) if ignore_automatic_stops else None
                override_optimisation_strategy = (
                    override_optimisation_strategies.get(optimiser.name, None) if override_optimisation_strategies else None
                )

                try:
                    optimiser.analyse_batch()
                    optimiser.generate_next_batch(
                        override_next=override_next,
                        ignore_automatic_stop=ignore_automatic_stop,
                        override_optimisation_strategy=override_optimisation_strategy,
                    )
                except FileNotFoundError:
                    # cant find the output file to analyse for batch.
                    pretty_print("\tNo output file to analyse yet.", color=TextColor.WARNING)
                    stop_iter_batch_dict[opt_name] = True

                except LookupError:
                    # optimiser has finished and there is no files registred.
                    pretty_print("\toptimiser has finished.", color=TextColor.GREEN)
                    stop_iter_batch_dict[opt_name] = True

                except Exception as e:
                    # other error not related to iter_batches to pass through and raise
                    raise e
