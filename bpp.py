"""Bin packing problem model."""

from __future__ import annotations
from dataclasses import dataclass, field
from math import ceil
from copy import deepcopy
from functools import lru_cache
import files


@dataclass(frozen=True, eq=True)
class BPInstance:
    """All the inputs needed to describe a Bin Packing Problem"""
    bin_size: float
    items: tuple[float]

    def __post_init__(self):
        """Cast self.transfers to a frozenset, allowing instantiating class with any iterable."""
        # https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(self, 'items', tuple(self.items))

    @classmethod
    def from_reader(cls, reader: files.InstanceReader):
        instance = cls(reader.bin_size, reader.items)
        # Save file path for later introspection
        object.__setattr__(instance, 'source', reader.path)
        return instance

    def __iter__(self):
        """Allows easier iteration."""
        return self.items.__iter__()

    def sort_decreasing(self) -> BPInstance:
        """Returns new instance with items sorted."""
        items = sorted(self.items, reverse=True)
        sorted_instance = self.__class__(self.bin_size, items)
        return sorted_instance

    @property
    @lru_cache
    def lower_bound(self) -> int:
        """Minimun number of bins required."""
        return ceil(sum(self.items) / self.bin_size)


@dataclass(eq=False)
class Bin:
    """Some properties and methods are cached to reduce computation time.
    Cache must be cleared when the Bin changes (item added or removed).
    """
    size: float
    items: list[float] = field(default_factory=list)
    closed: bool = False

    def __iter__(self):
        """Allows easier iteration."""
        return self.items.__iter__()

    def append(self, item) -> None:
        if item <= 0:
            raise ValueError("Item weight must be bigger than zero.")
        self._clear_cache()
        self.items.append(item)

    def pop(self, index) -> float:
        self._clear_cache()
        return self.items.pop(index)

    def remove(self, item) -> None:
        self._clear_cache()
        self.items.remove(item)

    @lru_cache
    def fits(self, item) -> bool:
        return item <= self.gap

    @property
    @lru_cache
    def gap(self) -> float:
        return (self.size - self.content)

    @property
    @lru_cache
    def content(self) -> float:
        return sum(self.items)

    def _clear_cache(self):
        self.__class__.fits.cache_clear()
        self.__class__.gap.fget.cache_clear()   # .fget needed because its a property
        self.__class__.content.fget.cache_clear()

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    @property
    def is_full(self) -> bool:
        return self.content == self.size


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
