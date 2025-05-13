from abc import ABC, abstractmethod


class IExecuter(ABC):
    @abstractmethod
    def execute(self):
        pass