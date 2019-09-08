from abc import ABC, abstractmethod


class BaseParser(ABC):
    def __init__(self, dmm):
        self.dmm = dmm

    @classmethod
    @abstractmethod
    def load(cls, dmm):
        raise NotImplementedError
