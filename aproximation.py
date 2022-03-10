"""Aproximation algorithms for bin packing problem."""

from abc import ABC, abstractmethod

import bpp
from draw import plot


class Algorithm(ABC):
    """Interface for every Bin Packing Approximation Algorithms."""
    instance: bpp.BPInstance
    solution: bpp.BPSolution

    def __init__(self, instance: bpp.BPInstance, debug=False) -> None:
        self.instance = instance

        # Initialize empty solution
        self.solution = bpp.BPSolution(instance.bin_size)

        self.debug = debug

    def maybe_plot(self):
        # TODO: aver que hago con esto
        if self.debug:
            plot(self.solution)
            input("Press Enter to continue...")

    @abstractmethod
    def solve(self) -> bpp.BPSolution:
        pass


class AlgorithmDecreasing(Algorithm):
    def __init__(self, instance: bpp.BPInstance) -> None:
        super().__init__(instance.sort_decreasing())


class WorstAlgorithm(Algorithm):
    """Usefull for testing. Puts each item in a new bin."""

    def solve(self) -> bpp.BPSolution:
        for item in self.instance:
            self.solution.pack_in_new_bin(item)
        return self.solution


class NextFitAlgorithm(Algorithm):
    """When the new item does not fit into the current bin,
    it closes it and opens a new bin.
    """

    def solve(self) -> bpp.BPSolution:
        for item in self.instance:
            last_bin = self.solution.last_bin
            if last_bin.fits(item):
                last_bin.append(item)
            else:
                last_bin.closed = True
                self.solution.pack_in_new_bin(item)
            self.maybe_plot()
        return self.solution


class FirstFitAlgorithm(Algorithm):
    """It attempts to place each new item into the first bin in which it fits."""

    def solve(self) -> bpp.BPSolution:
        for item in self.instance:
            for bin in self.solution:
                if bin.fits(item):
                    bin.append(item)
                    break
            else:   # item did not fit in any existing bin
                self.solution.pack_in_new_bin(item)
            self.maybe_plot()
        return self.solution


class FirstFitDecreasingAlgorithm(AlgorithmDecreasing, FirstFitAlgorithm):
    """Same as first fit, but initial list of items is sorted in decreasing order."""


class MinimumBinSlack(AlgorithmDecreasing):

    def solve(self) -> bpp.BPSolution:
        pass
        # items_remaining = self.instance.copy()
        # TODO: implement
