from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class InstanceReader:
    """Read instance from file."""
    path: Path

    def __post_init__(self):
        """Save basic info from header."""
        with self.path.open(mode='r') as file:
            self.number_of_items = self.number(file.readline())
            self.bin_size = self.number(file.readline())

    @property
    def items(self):
        """Lazy read items from file."""
        with self.path.open(mode='r') as file:
            _ = next(file)      # Skip first line
            _ = next(file)      # Skip second line
            for line in file:
                yield self.number(line)

    @staticmethod
    def number(s: str):
        """Cast string to number."""
        try:
            return int(s)
        except ValueError:
            return float(s)


class Instances:
    """Helper class to explore the ./instances/ folder."""
    parent_folder = Path('instances')
    easy_threshold = 150
    hard_threshold = 500

    @classmethod
    def all(cls) -> Iterator[InstanceReader]:
        return (InstanceReader(file) for file in cls.find_all_files(cls.parent_folder))

    @classmethod
    def easy(cls) -> Iterator[InstanceReader]:
        return (instance for instance in cls.all()
                if instance.number_of_items <= cls.easy_threshold)

    @classmethod
    def medium(cls) -> Iterator[InstanceReader]:
        return (instance for instance in cls.all()
                if cls.easy_threshold <= instance.number_of_items <= cls.hard_threshold)

    @classmethod
    def hard(cls) -> Iterator[InstanceReader]:
        return (instance for instance in cls.all()
                if cls.hard_threshold <= instance.number_of_items)

    @classmethod
    def hard28(self) -> Iterator[InstanceReader]:
        return (InstanceReader(file) for file in self.find_all_files(self.parent_folder/'Hard28'))

    @classmethod
    def falkenauer(self) -> Iterator[InstanceReader]:
        return (InstanceReader(file)
                for file in self.find_all_files(self.parent_folder/'Falkenauer'))

    def find_all_files(path):
        yield from path.rglob('*.*')
