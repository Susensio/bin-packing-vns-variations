"""Bin packing problem model."""

from __future__ import annotations
from dataclasses import dataclass, field
from math import ceil
from copy import deepcopy


@dataclass
class BPInstance:
    bin_size: float
    items: list[float]

    def __iter__(self):
        """Allows easier iteration."""
        return self.items.__iter__()

    def sort_decreasing(self) -> BPInstance:
        """Returns new instance with items sorted."""
        items = sorted(self.items, reverse=True)
        sorted_instance = self.__class__(self.bin_size, items)
        return sorted_instance

    def lower_bound(self) -> int:
        """Minimun number of bins required."""
        return ceil(sum(self.items) / self.bin_size)


@dataclass
class Bin:
    size: float
    items: list[float] = field(default_factory=list)
    closed: bool = False

    def __iter__(self):
        """Allows easier iteration."""
        return self.items.__iter__()

    def append(self, item) -> None:
        if item <= 0:
            raise ValueError("Item weight must be bigger than zero.")
        self.items.append(item)

    def pop(self, index) -> float:
        return self.items.pop(index)

    def remove(self, item) -> None:
        self.items.remove(item)

    def fits(self, item) -> bool:
        return item <= (self.size - self.content)

    @property
    def is_empty(self) -> bool:
        return self.content == 0

    @property
    def is_full(self) -> bool:
        return self.content == self.size

    @property
    def content(self) -> float:
        return sum(self.items)


@dataclass
class BPSolution:
    bin_size: float
    bins: list[Bin] = field(default_factory=list)

    def __post_init__(self):
        """Always add first empty bin."""
        self.add_empty_bin()

    def add_empty_bin(self) -> None:
        self.bins.append(Bin(self.bin_size))

    def __iter__(self):
        """Allows easier iteration."""
        return self.bins.__iter__()

    def __getitem__(self, index):
        return self.bins[index]

    def __len__(self):
        return self.bins.__len__()

    @property
    def last_bin(self) -> Bin:
        return self.bins[-1]

    def pack_in_new_bin(self, item) -> None:
        """Do not create new bin if last one is empty."""
        if self.last_bin.is_empty:
            self.last_bin.append(item)
        else:
            new_bin = Bin(self.bin_size)
            new_bin.append(item)
            self.bins.append(new_bin)

    def move_item(self, bin_from, item, bin_to) -> None:
        self.bins[bin_from].remove(item)
        self.bins[bin_to].append(item)

    def remove_empty_bins(self):
        self.bins = [b for b in self.bins if not b.is_empty]

    def copy(self):
        return deepcopy(self)
