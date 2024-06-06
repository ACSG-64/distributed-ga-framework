from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

from shared.models.entities.individual import IndividualEntity
from worker.experimenter.coordinator.implementation import NextCallback

T = TypeVar('T')


class IEvaluator(ABC, Generic[T]):
    @abstractmethod
    def evaluate_sample(self, sample: List[IndividualEntity[T]], _next: NextCallback) -> None:
        raise NotImplementedError
