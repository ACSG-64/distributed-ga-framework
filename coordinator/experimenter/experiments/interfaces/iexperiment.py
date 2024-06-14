from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

from coordinator.experimenter.annotations.callbacks import NextCallback, StopCallback
from shared.models.value_objects.individual import IndividualValue

T = TypeVar('T')


class IExperiment(ABC, Generic[T]):
    @abstractmethod
    def apply_genetic_operations(self, generation_number: int,
                                 population: List[IndividualValue[T]],
                                 _next: NextCallback, _stop: StopCallback) -> None:
        """
        Receives an evaluated population in order to create a new generation.
        :param generation_number: The current generation
        :param population: evaluated population
        :param _next: callback to proceed with the created population after applying GA operations
        :param _stop: callback to terminate the experimentation process
        """
        raise NotImplementedError
