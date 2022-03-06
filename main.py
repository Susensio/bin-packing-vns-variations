
from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from math import ceil
# from random import Random

from draw import plot
import vns


@dataclass
class BPInstance:
    bin_size: float
    items: list[float]

    def __iter__(self):
        return self.items.__iter__()

    def sort_decreasing(self):
        items = sorted(self.items, reverse=True)
        sorted_instance = self.__class__(self.bin_size, items)
        return sorted_instance

    def lower_bound(self):
        """Minimun number of bins required."""
        return ceil(sum(self.items) / self.bin_size)


@dataclass
class Bin:
    size: float
    items: list[float] = field(default_factory=list)
    closed: bool = False

    def add(self, item):
        self.items.append(item)

    def fits(self, item):
        return item <= (self.size - self.content)

    @property
    def content(self):
        return sum(self)

    def __iter__(self):
        return self.items.__iter__()


@dataclass
class BPSolution:
    bin_size: float
    bins: list[Bin] = field(default_factory=list)

    def __post_init__(self):
        """Add first empty bin."""
        self.bins.append(Bin(self.bin_size))

    def pack_in_new_bin(self, item):
        new_bin = Bin(self.bin_size, [item])
        self.bins.append(new_bin)

    def __iter__(self):
        return self.bins.__iter__()

    def __getitem__(self, index):
        return self.bins[index]

    @property
    def fitness(self):
        """A good solution will always have nearly full bins.
        fitness = mean squared occupancy.
        ranges from 0 to 1, 1 being all bins are full.
        """
        return (sum((bin.content/bin.size)**2
                    for bin in self.bins)
                / len(self.bins))

    def shake(self):
        pass

    def print_stats(self):
        print(f"Number of bins = {len(self.bins)} \tFitness = {self.fitness:.3f}")

    # def pretty_print(self):
    #     for bin in self.bins:
    #         line = ["["]
    #         for item in bin.items:
    #             if item == 1:
    #                 # line.append("┃")⊏═⊐⊡
    #                 line.append("⊡")
    #             else:
    #                 # line.append("┣")
    #                 line.append("⊏")
    #                 for _ in range(item-2):
    #                     # line.append("━")
    #                     line.append("🟰")
    #                 # line.append("┫")
    #                 line.append("⊐")
    #         line.append(" "*(self.bin_size-len(line)+1))
    #         line.append("]")
    #         print("".join(line))


@dataclass
class BPOptimizer(vns.NeighbourhoodExplorer):
    solution: BPSolution
    instance: BPInstance

    def shake(self, k: int) -> BPOptimizer:
        pass

    def improve(self) -> BPOptimizer:
        pass

    @property
    def fitness(self) -> float:
        return self.solution.fitness


class BPAlgorithm(ABC):
    """Interface for every Bin Packing Approximation Algorithms."""
    instance: BPInstance
    solution: BPSolution

    def __init__(self, instance: BPInstance, decreasing: bool = False) -> None:
        if decreasing:
            instance = instance.sort_decreasing()
        self.instance = instance

        # Initialize empty solution
        self.solution = BPSolution(instance.bin_size)

    @ abstractmethod
    def solve(self) -> BPSolution:
        pass


class NextFitAlgorithm(BPAlgorithm):
    """When the new item does not fit into the current bin,
    it closes it and opens a new bin.
    """

    def solve(self) -> BPSolution:
        for item in self.instance:
            last_bin = self.solution[-1]
            if last_bin.fits(item):
                last_bin.add(item)
            else:
                last_bin.closed = True
                self.solution.pack_in_new_bin(item)

        return self.solution


class FirstFitAlgorithm(BPAlgorithm):
    """It attempts to place each new item into the first bin in which it fits."""

    def solve(self) -> BPSolution:
        for item in self.instance:
            for bin in self.solution:
                if bin.fits(item):
                    bin.add(item)
                    break
            else:
                self.solution.pack_in_new_bin(item)

        return self.solution


class FirstFitDecreasingAlgorithm(FirstFitAlgorithm):
    """Same as first fit, but initial list of items is sorted in decreasing order."""

    def __init__(self, instance: BPInstance) -> None:
        super().__init__(instance, decreasing=True)


# def first_fit_decreasing(instance: BPInstance):
#     solution = first_fit(instance.sort_decreasing())
#     print(f"First fit decreasing: {len(solution.bins)=}")
#     return solution


# def next_fit(instance: BPInstance):
#     solution = BPSolution(instance.bin_size)

#     for item in instance:
#         last_bin = solution[-1]
#         if last_bin.fits(item):
#             last_bin.add(item)
#         else:
#             last_bin.closed = True
#             solution.pack_in_new_bin(item)
#     # solution.pretty_print()
#     print(f"Next fit: {len(solution.bins)=}")
#     return solution


# def first_fit(instance: BPInstance):
#     solution = BPSolution(instance.bin_size)

#     for item in instance:
#         for bin in solution:
#             if bin.fits(item):
#                 bin.add(item)
#                 break
#         else:
#             solution.pack_in_new_bin(item)

#     # solution.pretty_print()
#     print(f"First fit: {len(solution.bins)=}")
#     return solution

# test_instance = BPInstance(10, [1, 5, 2, 8, 6, 2, 3, 4, 5, 8, 1, 1, 2, 3])

# bin_size = 200
# test_instance = BPInstance(
#     bin_size, [bin_size*random()*0.5 for _ in range(int(bin_size))])

if __name__ == "__main__":

    test_instance = BPInstance(
        10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5])

    for Algorithm in (
        NextFitAlgorithm,
        FirstFitAlgorithm,
        FirstFitDecreasingAlgorithm,
    ):
        alg = Algorithm(test_instance)
        sol = alg.solve()
        sol.print_stats()
        plot(sol)
