from enum import Enum
from typing import Generic, List, Tuple, TypeVar

from shared.models.value_objects.individual import IndividualValue
from shared.annotations.custom import UUID
from coordinator.services.storage.abstract.storage import StorageAdapter

T = TypeVar('T')


class ExperimentIntegrityViolations(Enum):
    EXPERIMENT_NON_EXISTENT = 1
    NO_GENERATIONS = 2
    NO_POPULATION = 3


class ExperimentSetupHelper(Generic[T]):
    @classmethod
    def setup(cls, experiment_name: str, storage: StorageAdapter[T],
              initial_population_encodings: List[IndividualValue[T]]) -> Tuple[UUID, bool]:
        """
        Creates and stores the experiment information along with the initial population. If
        there is already another experiment with the same name, it will finish the remaining
        initialization steps. If the experiment already exists and is fully initialized, no
        actions will be taken
        :param experiment_name: the name for the new experiment
        :param storage: storage adapter
        :param initial_population_encodings:
        :return: The UUID of the experiment and True if the passed population was stored as the initial population,
        otherwise False meaning that the population already stored will be used instead
        """
        # Create a new experiment in the storage
        experiment_id, _ = storage.create_experiment(experiment_name)
        # Check integrity
        is_valid, problem = cls.validate(experiment_id, storage)
        if is_valid:  # return the experiment id and do nothing else because it is already integral
            return experiment_id, False
        # Create a generation if it doesn't exist or get the latest one
        generation_id: UUID = storage.create_generation(experiment_id) \
            if problem.NO_GENERATIONS \
            else storage.get_latest_generation_id(experiment_id)
        if problem.NO_POPULATION or problem.NO_GENERATIONS:
            # Store the initial population
            storage.store_population(generation_id, initial_population_encodings)
            return experiment_id, True
        return experiment_id, False

    @classmethod
    def validate(cls, experiment_id, storage: StorageAdapter[T]) \
            -> Tuple[bool, ExperimentIntegrityViolations | None]:
        """
        Checks if an experiment is correctly initialized and if not, what steps are missing
        :param experiment_id: the UUID of the experiment
        :param storage:
        :return: Integrity violation
        """
        if not storage.experiment_exist(experiment_id):  # the experiment must exist
            return False, ExperimentIntegrityViolations.EXPERIMENT_NON_EXISTENT
        generation_id = storage.get_latest_generation_id(experiment_id)
        if not generation_id:  # there must be at least one generation
            return False, ExperimentIntegrityViolations.NO_GENERATIONS
        has_population = len(storage.get_population(generation_id)) > 0  # is there a population
        if not has_population:
            return False, ExperimentIntegrityViolations.NO_POPULATION
        return True, None
