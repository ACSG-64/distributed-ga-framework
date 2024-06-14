from abc import ABC, abstractmethod
from typing import Tuple, List, Generic, TypeVar

from shared.annotations.custom import UUID, FitnessScore
from shared.models.entities.individual import IndividualEntity
from shared.models.value_objects.individual import IndividualValue

T = TypeVar('T')


class IStorage(ABC, Generic[T]):
    @abstractmethod
    def create_experiment(self, name: str) -> Tuple[UUID, bool]:
        raise NotImplementedError

    @abstractmethod
    def experiment_exist(self, experiment_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_generation(self, experiment_id: UUID) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def store_population(self, generation_id: UUID, individuals: List[IndividualValue[T]]):
        raise NotImplementedError

    @abstractmethod
    def store_individual_fitness(self, individual_id: UUID, fitness: FitnessScore):
        raise NotImplementedError

    @abstractmethod
    def get_experiment_id(self, experiment_name: str) -> UUID | None:
        raise NotImplementedError

    @abstractmethod
    def get_latest_generation_id(self, experiment_id: UUID) -> UUID | None:
        raise NotImplementedError

    @abstractmethod
    def get_individual(self, individual_id: UUID) -> IndividualEntity[T] | None:
        raise NotImplementedError

    @abstractmethod
    def get_population(self, generation_id: UUID) -> List[IndividualEntity[T]]:
        raise NotImplementedError

    @abstractmethod
    def get_non_evaluated_individuals(self, generation_id: UUID) -> List[IndividualEntity[T]]:
        raise NotImplementedError

    @abstractmethod
    def count_generations(self, experiment_id: UUID) -> int:
        raise NotImplementedError
