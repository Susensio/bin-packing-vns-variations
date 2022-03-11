from pathlib import Path

INSTANCES = Path('instances')

example = next(next(next(INSTANCES.iterdir()).iterdir()).iterdir())


class InstanceReader:
    def __init__(self, path) -> None:
        self.path = Path(path)

    def read(self):
        with open(self.path, 'r') as f:
            n = self.number(f.readline())
            self.bin_size = self.number(f.readline())
            self.items = [self.number(n) for n in f.readlines()]
            assert len(self.items) == n

        return self

    @ staticmethod
    def number(s: str):
        try:
            return int(s)
        except ValueError:
            return float(s)


ins = InstanceReader(example)
