from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import process_time
# from loguru import logger
from enum import Enum, auto

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
    def stats(self):
        """Returns a string with usefull information about the current solution."""


class LocalSearchStrategy(Enum):
    FIRST = auto()
    BEST = auto()


@logs.append_logger
@dataclass
class VNS(ABC):
    explorer: NeighbourhoodExplorer
    k_max: int
    t_max: float    # seconds

    k: int = field(default=1, init=False)

    def solve(self) -> NeighbourhoodExplorer:
        self.start_timer()

        self.logger.info(f"{self.__class__.__name__}({getattr(self,'strategy','')})\t"
                         f"{self.explorer.stats}")

        while True:
            self.k = 1
            while self.k <= self.k_max:
                self.logger.debug(f"Neighbourhood = {self.k}")

                self.do_steps()     # The algorithm core

                if self.timed_out:
                    self.logger.info(f"Timeout. {self.elapsed_time=:.2f}s")
                    self.logger.success(f"{self.__class__.__name__}"
                                        f"({getattr(self,'strategy','')})\t"
                                        f"{self.explorer.stats}")
                    return self.explorer.solution

            self.logger.info("Restart neighbourhood search")
            self.logger.debug(f"{self.elapsed_time}")

    @abstractmethod
    def do_steps(self) -> None:
        """This is where each concrete algorithm gets implemented."""

    def start_timer(self) -> None:
        self.t_0 = process_time()

    @property
    def elapsed_time(self) -> float:
        return process_time() - self.t_0

    @property
    def timed_out(self) -> bool:
        return self.elapsed_time >= self.t_max

    def neighbourhood_change_sequential(self, new_explorer: NeighbourhoodExplorer) -> None:
        """Reused in many algorithms."""
        if new_explorer.fitness > self.explorer.fitness:
            self.explorer = new_explorer
            self.logger.debug(self.explorer.stats)
            plot(self.explorer.solution)

            self.k = 1
        else:
            self.k += 1


@dataclass
class BasicVNS(VNS):
    strategy: LocalSearchStrategy = LocalSearchStrategy.BEST

    def do_steps(self):
        neighbour = self.explorer.shake(self.k)
        local_optimum = neighbour.improve(self.strategy)
        self.neighbourhood_change_sequential(local_optimum)


class ReducedVNS(VNS):
    """Same as BasicVNS but improvement phase is discarded."""

    def do_steps(self):
        neighbour = self.explorer.shake(self.k)
        self.neighbourhood_change_sequential(neighbour)


class VNDescent(VNS):
    """Same as BasicVNS but improvement phase is discarded."""

    def do_steps(self):
        neighbour = self.explorer.shake(self.k)
        local_optimum = neighbour.improve(self.strategy)
        self.neighbourhood_change_sequential(local_optimum)
