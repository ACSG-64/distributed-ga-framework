from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

from shared.models.entities.individual import IndividualEntity
from coordinator.experimenter.coordinator.implementation import NextCallback, StopCallback

T = TypeVar('T')


class IExperiment(ABC, Generic[T]):
    @abstractmethod
    def apply_genetic_operations(self, population: List[IndividualEntity[T]],
                                 _next: NextCallback, _stop: StopCallback) -> None:
        """
        Receives an evaluated population in order to create a new generation.
        :param population: evaluated population
        :param _next: callback to proceed with the created population after applying GA operations
        :param _stop: callback to terminate the experimentation process
        """
        raise NotImplementedError
