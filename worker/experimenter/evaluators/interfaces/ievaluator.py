from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

from shared.models.entities.individual import IndividualEntity
from worker.experimenter.annotations.callbacks import NextCallback

T = TypeVar('T')


class IEvaluator(ABC, Generic[T]):
    """
    Implement this interface for your custom evaluator
    """
    @abstractmethod
    def evaluate_sample(self, sample: List[IndividualEntity[T]], _next: NextCallback) -> None:
        """
        :param sample:
        :param _next: callback to send back the evaluated individuals
        :return:
        """
        raise NotImplementedError
