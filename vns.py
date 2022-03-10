from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import process_time


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
    def improve(self) -> NeighbourhoodExplorer:
        """Improve from current neighbour."""


@dataclass
class VNS(ABC):
    explorer: NeighbourhoodExplorer
    k_max: int
    t_max: float    # seconds

    k: int = field(init=False)

    def __post_init__(self):
        self.k = 1

    def neighbourhood_change_sequential(self, new_explorer: NeighbourhoodExplorer) -> None:
        if new_explorer.fitness > self.explorer.fitness:
            self.explorer = new_explorer
            # print(self.explorer.fitness)
            self.k = 1
        else:
            self.k += 1


class BasicVNS(VNS):
    def solve(self) -> None:
        start_time = process_time()
        self.k = 1
        while self.k <= self.k_max:
            print(self.k)
            print(process_time() - start_time)
            print("SHAKE")
            neighbour = self.explorer.shake(self.k)
            print("IMPROVE")
            local_optimum = neighbour.improve()
            self.neighbourhood_change_sequential(local_optimum)

            elapsed = (process_time() - start_time)
            if elapsed > self.t_max:
                break

        self.explorer.print_stats()
        return self.explorer
