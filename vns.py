from __future__ import annotations
from abc import ABC, abstractmethod


class NeighbourhoodExplorer(ABC):
    @abstractmethod
    def shake(self, k: int) -> NeighbourhoodExplorer:
        """Returns a random kth neighbour."""

    @abstractmethod
    def improve(self) -> NeighbourhoodExplorer:
        """Improve from current neighbour."""

    @property
    @abstractmethod
    def fitness(self) -> float:
        pass


class VNS(ABC):
    pass
