from abc import ABC, abstractmethod


class Optimizer(ABC):
    @abstractmethod
    def shake(self):
        pass

    @abstractmethod
    def improve(self):
        pass


class VNS(ABC):
    pass
