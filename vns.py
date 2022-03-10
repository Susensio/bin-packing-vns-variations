from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import process_time
from loguru import logger
from enum import Enum, auto

from draw import plot


class NeighbourhoodExplorer(ABC):
    @property
    @abstractmethod
    def fitness(self) -> float:
        pass

    @abstractmethod
    def shake(self, k: int) -> NeighbourhoodExplorer:
        """Returns a random kth neighbour."""
        # TODO: y si no encuentro ningun vecino???

    @abstractmethod
    def improve(self, strategy: LocalSearchStrategy) -> NeighbourhoodExplorer:
        """Improve from current neighbour."""


class LocalSearchStrategy(Enum):
    FIRST = auto()
    BEST = auto()


@dataclass
class VNS(ABC):
    explorer: NeighbourhoodExplorer
    k_max: int
    t_max: float    # seconds

    k: int = field(default=1, init=False)

    def solve(self) -> NeighbourhoodExplorer:
        self.start_timer()

        logger.info(f"{self.__class__.__name__}({getattr(self,'strategy','')})\t"
                    f"{self.explorer.stats}")

        while True:
            self.k = 1
            while self.k <= self.k_max:
                logger.debug(f"Neighbourhood = {self.k}")

                self.do_steps()     # The algorithm core

                if self.timed_out:
                    logger.warning(f"Timeout. {self.elapsed_time=:.2f}s")
                    logger.success((f"{self.__class__.__name__}({getattr(self,'strategy','')})\t"
                                    f"{self.explorer.stats}"))
                    return self.explorer.solution

            logger.info("Restart neighbourhood search")
            logger.debug(f"{self.elapsed_time}")

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
            logger.success(self.explorer.stats)
            plot(self.explorer.solution)
            # print(self.explorer.fitness)
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
