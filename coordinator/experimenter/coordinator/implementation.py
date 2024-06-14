import time
from threading import Thread
from typing import NamedTuple, TypeVar, Generic, List

from coordinator.experimenter.coordinator.annotations.callbacks import OnTestingPopReadyCb, OnPopulationTestedCb
from coordinator.experimenter.experiments.interfaces.iexperiment import IExperiment
from shared.annotations.custom import UUID, FitnessScore
from shared.models.value_objects.individual import IndividualValue
from coordinator.services.storage.interfaces.istorage import IStorage
from shared.utils.event_listener import EventListener
from shared.utils.observable_scalar import ObservableScalar


class FitnessResult(NamedTuple):
    id: UUID
    fitness: FitnessScore


T = TypeVar('T')


class ExperimentCoordinator(Generic[T]):
    def __init__(self, experiment_id: UUID,
                 experiment: IExperiment[T],
                 storage: IStorage[T],
                 max_time_between_results_secs=60):
        """
        :param experiment_id:
        :param experiment: an IExperiment implementation and its method, apply_genetic_operations,
        will be called when the population is evaluated
        :param storage:
        :param max_time_between_results_secs: This will be used in the timeout method
        """
        self._storage = storage
        self._ex_id: UUID = experiment_id
        self._experimenter = experiment
        self._max_time_between_results_secs = max_time_between_results_secs
        self._generation_id = self._storage.get_latest_generation_id(self._ex_id)
        self._pending_individuals: set[UUID] = set()
        self._latest_result_date: float | None = None
        self._is_busy = ObservableScalar[bool](False)
        self._is_terminated = ObservableScalar[bool](False)
        self._testing_sample_listeners = EventListener[OnTestingPopReadyCb[T]]()
        self._pop_tested_listeners = EventListener[OnPopulationTestedCb[T]]()
        self._new_gen_listeners = EventListener[OnPopulationTestedCb[T]]()
        self.__sync_and_get_untested_individuals()

    @property
    def is_busy(self):
        return self._is_busy

    @property
    def is_terminated(self):
        return self._is_terminated

    @property
    def untested_individuals(self):
        return self.__sync_and_get_untested_individuals()

    def stop(self):
        self._is_terminated.value = True
        self._pending_individuals.clear()  # clear pending individuals
        self._latest_result_date = None
        self._is_busy.value = False

    def add_individual_fitness(self, individual_id: UUID, fitness_score: FitnessScore):
        # Check if the individual's fitness was already stored
        if self._is_busy.value or individual_id not in self._pending_individuals:
            return
        # Store the fitness score
        self._storage.store_individual_fitness(individual_id, fitness_score)
        self._pending_individuals.remove(individual_id)  # update tracker
        self.__refresh_latest_result_date()  # update event tracker
        # Check if there are individuals that need to be tracked
        if len(self._pending_individuals) == 0:
            self.__stage_new_generation()

    def add_on_testing_sample_selected_listener(self, listener: OnTestingPopReadyCb[T]):
        """
        Listeners are notified when a new testing sample is selected, that is, when a new
        generation is created only the individuals that don't have a fitness assigned
        will be sent in order to be evaluated.
        :param listener:
        """
        self._testing_sample_listeners.add_listener(listener)
        return self

    def add_on_population_evaluated_listener(self, listener: OnTestingPopReadyCb[T]):
        """
        Listeners are notified when a population is fully evaluated
        :param listener:
        """
        self._pop_tested_listeners.add_listener(listener)
        return self

    def timeout(self, undelivered_individuals_count: int) -> bool:
        """
        Checks if too much time has elapsed since the last result arrived. This time period is
        defined in the constructor.
        This could be useful to determine whether to send again the pending individuals to the
        workers.
        :param undelivered_individuals_count: the number of individuals that are still pending
        to be received by workers
        :return: True if timeout, False otherwise
        """
        if self._is_busy.value or len(self._pending_individuals) == 0:
            return False
        if self._latest_result_date is None:
            self.__refresh_latest_result_date()
            return False
        current_time = time.time()
        time_elapsed = current_time - self._latest_result_date
        return (time_elapsed >= self._max_time_between_results_secs
                and undelivered_individuals_count == 0)

    def __stage_new_generation(self):
        self._is_busy.value = True
        current_population = self._storage.get_population(self._generation_id)
        self._pop_tested_listeners(current_population)
        population = [IndividualValue(encoding=ie.encoding, fitness=ie.fitness)
                      for ie in current_population]
        gen_number = self._storage.count_generations(self._ex_id)
        Thread(target=self._experimenter.apply_genetic_operations,
               args=(gen_number, population, self.__start_new_generation, self.stop,)
               ).start()

    def __start_new_generation(self, new_individuals: List[IndividualValue[T]]):
        # Create a new generation
        self._generation_id = self._storage.create_generation(self._ex_id)
        # Store the new population
        self._storage.store_population(self._generation_id, new_individuals)
        # Get the individuals that doesn't have a fitness assigned yet
        sample = self.__sync_and_get_untested_individuals()
        self.__refresh_latest_result_date()
        self._testing_sample_listeners(sample)
        self._is_busy.value = False

    def __sync_and_get_untested_individuals(self):
        pending_individuals = self._storage.get_non_evaluated_individuals(self._generation_id)
        self._pending_individuals.clear()  # clear pending individuals
        self._pending_individuals.update([ind.id for ind in pending_individuals])
        return pending_individuals

    def __refresh_latest_result_date(self):
        self._latest_result_date = time.time()
