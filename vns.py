from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto

import utils
import logs
from draw import plot


@logs.append_logger
class NeighbourhoodExplorer(ABC):

    @abstractmethod
    def shake(self, k: int) -> NeighbourhoodExplorer:
        """Returns a random kth neighbour."""

    @abstractmethod
    def improve(self, strategy: LocalSearchStrategy) -> NeighbourhoodExplorer:
        """Improve from current neighbour."""

    @property
    @abstractmethod
    def fitness(self) -> float:
        """Statistic that is being maximized in optimization."""

    @property
    @abstractmethod
    def is_optimum(self) -> bool:
        """If global optimum is reached and detected, inform to stop early."""

    @property
    @abstractmethod
    def stats(self):
        """Returns a string with usefull information about the current solution."""


class LocalSearchStrategy(Enum):
    FIRST = auto()
    BEST = auto()

    def __repr__(self) -> str:
        return self.name


@logs.append_logger
@dataclass
class VNS(ABC):
    explorer: NeighbourhoodExplorer = field(repr=False)
    k_max: int
    t_max: float    # seconds

    local_strategy: LocalSearchStrategy = None

    # To keep track of current neighbourhood
    k: int = field(default=1, init=False, repr=False)
    timer: utils.Timer = field(default_factory=utils.Timer, init=False, repr=False)

    def solve(self) -> NeighbourhoodExplorer:
        # TODO: improve timeout with context manager maybe?
        self.timer.start()

        # self.logger.info(f"{self.__class__.__name__}({getattr(self,'strategy','')})\t"
        #                  f"{self.explorer.stats}")
        self.logger.info(self)
        self.logger.info(f"{self.explorer.stats}")

        stop = False
        while not stop:
            self.k = 1
            while self.k <= self.k_max:
                self.logger.debug(f"Neighbourhood = {self.k}")

                self.do_steps()     # The algorithm core

                if self.explorer.is_optimum:
                    stop = True
                    self.logger.info("Global optimum found.")
                    break

                if self.timed_out:
                    stop = True
                    self.logger.info(f"Timeout. {self.timer.elapsed_time=:.2f}s")
                    break

            else:   # If the inner loop wasn't broken
                self.logger.info("Restart neighbourhood search")
                self.logger.debug(f"{self.timer.elapsed_time}")

        self.logger.success(f"{self.__class__.__name__}"
                            f"({getattr(self,'strategy','')})\t"
                            f"{self.explorer.stats}")

        self.timer.stop()
        return self.explorer.solution

    @abstractmethod
    def do_steps(self) -> None:
        """This is where each concrete algorithm gets implemented."""

    @property
    def elapsed_time(self) -> float:
        return self.timer.elapsed_time

    @property
    def timed_out(self) -> bool:
        return self.timer.elapsed_time >= self.t_max

    def neighbourhood_change_sequential(self, new_explorer: NeighbourhoodExplorer) -> None:
        """Reused in many algorithms."""
        if new_explorer.fitness > self.explorer.fitness:
            self.explorer = new_explorer
            self.logger.debug(self.explorer.stats)
            # plot(self.explorer.solution)

            self.k = 1
        else:
            self.k += 1


class BasicVNS(VNS):

    def do_steps(self):
        neighbour = self.explorer.shake(self.k)
        local_optimum = neighbour.improve(self.local_strategy)
        self.neighbourhood_change_sequential(local_optimum)


class ReducedVNS(VNS):
    """Same as BasicVNS but improvement phase is discarded."""

    def do_steps(self):
        neighbour = self.explorer.shake(self.k)
        self.neighbourhood_change_sequential(neighbour)


# class GeneralVNS(VNS):
#     """VND used as an improvement procedure."""

#     def do_steps(self):
#         neighbour = self.explorer.shake(self.k)
#         local_optimum = neighbour.improve(self.strategy)
#         self.neighbourhood_change_sequential(local_optimum)
