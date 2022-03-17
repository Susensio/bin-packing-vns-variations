from __future__ import annotations
from typing import Iterator
from dataclasses import dataclass
from copy import deepcopy
import random

from draw import plot

import vns
import bpp


@dataclass(frozen=True, slots=True)
class Transfer:
    bin_from_index: int
    item: int
    bin_to_index: int

    @classmethod
    def reversed(cls, t: Transfer) -> Transfer:
        """Returns the opposite Transfer that would undo `t`"""
        return cls(
            t.bin_to_index,
            t.item,
            t.bin_from_index
        )


@dataclass(frozen=True, eq=True)
class Move:
    """A Move is a sequence of transfers."""
    transfers: frozenset[Transfer]

    def __post_init__(self):
        """Cast self.transfers to a frozenset, allowing instantiating class with any iterable."""
        # https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(self, 'transfers', frozenset(self.transfers))

    def __iter__(self):
        return self.transfers.__iter__()

    def __len__(self):
        return self.transfers.__len__()

    @classmethod
    def from_transfer(cls, bin_from_index: int, item: float, bin_to_index: int) -> Move:
        transfers = {Transfer(bin_from_index, item, bin_to_index)}
        return cls(transfers)

    @classmethod
    def from_swap(cls,
                  bin_first_index: int, item_first: float,
                  bin_second_index: int, item_second: float
                  ) -> Move:
        """A swap is compossed of two transfers."""

        transfers = {Transfer(bin_first_index, item_first, bin_second_index),
                     Transfer(bin_second_index, item_second, bin_first_index)}
        return cls(transfers)

    @classmethod
    def reversed(cls, m: Move) -> Move:
        """Returns the opposite Move that would undo `m`"""
        return cls({Transfer.reversed(t) for t in m.transfers})


@dataclass
class BPSolutionExplorer(vns.NeighbourhoodExplorer):
    """Wraps BPSolution with exploring capabilities needed for neighbourhood searching."""
    instance: bpp.BPInstance
    solution: bpp.BPSolution

    @property
    def fitness(self) -> float:
        """A good solution will always have nearly full bins.
        fitness = sum of squared occupancy.
        """
        return sum(bin.content**2 for bin in self.solution)

    @property
    def is_optimum(self) -> bool:
        return self.instance.lower_bound == len(self.solution.bins)

    def delta_fitness_from_move(self, move: Move) -> float:
        """How much would fitness change if move were applied.
        This partial calculation improves substantially computation time.
        Source:
        Fleszar2002 - New heuristics for one-dimensional bin-packing
        """
        if len(move) == 1:  # Transfer
            [transfer] = move   # unpack only transfer from move
            b1 = self.solution[transfer.bin_from_index].content
            b2 = self.solution[transfer.bin_to_index].content
            it = transfer.item
            return (b1-it)**2 + (b2+it)**2 - b1**2 - b2**2

        else:               # Swap
            [trans1, trans2] = move
            b1 = self.solution[trans1.bin_from_index].content
            i1 = trans1.item
            b2 = self.solution[trans2.bin_from_index].content
            i2 = trans2.item
            return (b1 - i1 + i2)**2 + (b2 + i1 - i2)**2 - b1**2 - b2**2

    def shake(self, k_neighbourhood: int) -> BPSolutionExplorer:
        """This could be improved with better termination conditions from paper Fleszar2002.
        Furthermore, if random choice is to be made, there is no need to generate all moves.
        """
        self.logger.debug(f"SHAKING... {k_neighbourhood=}")
        new_solution = self.copy()

        # Save applied moves to avoid looping back to the same solution
        moves_applied_reversed = set()

        for kth in range(k_neighbourhood):
            # Only chose between moves that won't undo previous moves
            moves = [m for m in new_solution.possible_moves()
                     if m not in moves_applied_reversed]
            self.logger.trace(f"{kth=}\t{len(moves)=}")

            if len(moves) == 0:
                break
            move = random.choice(moves)

            new_solution.do_move(move)
            moves_applied_reversed.add(Move.reversed(move))

        return new_solution

    def improve(self, strategy: vns.LocalSearchStrategy) -> BPSolutionExplorer:
        """Stop iterating when improvement is no longer possible."""
        self.logger.debug(f"IMPROVING...  {strategy.name=}")
        new_solution = self.copy()

        while True:
            moves = new_solution.possible_moves(skip_full_bins=True)

            if strategy == vns.LocalSearchStrategy.BEST:
                best_move = max(moves, key=new_solution.delta_fitness_from_move,
                                default=None)

            elif strategy == vns.LocalSearchStrategy.FIRST:
                best_move = next((m for m in moves
                                  if new_solution.delta_fitness_from_move(m) > 0),
                                 None)  # default

            if (best_move is None) or (new_solution.delta_fitness_from_move(best_move) <= 0):
                self.logger.trace("No improvement found.")
                break

            self.logger.trace("Improvement found!")
            new_solution.do_move(best_move)
            self.logger.trace(f"{new_solution.stats}")
            # plot(new_solution.solution)

        return new_solution

    def possible_moves(self, skip_full_bins: bool = False) -> Iterator[Move]:
        """When in an improvement phase, full bins are skiped as they do not increase fitness."""
        yield from self.possible_transfers(skip_full_bins)
        yield from self.possible_swaps(skip_full_bins)

    def possible_transfers(self, skip_full_bins: bool) -> Iterator[Move]:
        """Enumerates exhaustively every possible transfer, without repetition."""
        for bin_from_index, bin_from in enumerate(self.solution):

            if skip_full_bins and bin_from.is_full:   # Skip full bins when needed
                continue

            for item in bin_from:
                for bin_to_index, bin_to in enumerate(self.solution):

                    if bin_from_index == bin_to_index:  # Do not transfer to same bin
                        continue

                    if bin_to.fits(item):
                        yield Move.from_transfer(bin_from_index, item, bin_to_index)

    def possible_swaps(self, skip_full_bins: bool) -> Iterator[Move]:
        """Enumerates exhaustively every possible swap, without repetition."""
        for bin_first_index, bin_first in enumerate(self.solution):

            if (skip_full_bins and bin_first.is_full):   # Skip full bins when needed
                continue

            for item_first in bin_first:
                for bin_second_index, bin_second in enumerate(self.solution):

                    if skip_full_bins and bin_second.is_full:   # Skip full bins when needed
                        continue

                    # Do not swap backwards (avoid duplicated moves)
                    if bin_first_index >= bin_second_index:
                        continue

                    for item_second in bin_second:

                        if item_first == item_second:   # Do not swap equal items
                            continue

                        if (    # Swap is possible: both items would fit without the other
                            bin_first.fits(item_second - item_first) and
                            bin_second.fits(item_first - item_second)
                        ):

                            yield Move.from_swap(bin_first_index, item_first,
                                                 bin_second_index, item_second)

    def do_move(self, move) -> BPSolutionExplorer:
        """Perform move on solution INPLACE, returns self for convinience."""
        for transfer in move:
            self.solution.move_item(transfer.bin_from_index,
                                    transfer.item,
                                    transfer.bin_to_index)
        self.solution.remove_empty_bins()
        return self

    def copy(self):
        return deepcopy(self)

    @property
    def stats(self):
        return f"Bins={len(self.solution)}(min={self.instance.lower_bound}) Fitness={self.fitness}"

    def print_stats(self):
        print(self.stats)

    def plot(self):
        return plot(self.solution)
