import time
from threading import Thread
from typing import TypeVar, Generic, List

from shared.models.entities.individual import IndividualEntity
from shared.utils.event_listener import EventListener
from shared.utils.observable_scalar import ObservableScalar
from worker.experimenter.coordinator.annotations.callbacks import OnEvaluationCompleteCb
from worker.experimenter.evaluators.interfaces.ievaluator import IEvaluator

T = TypeVar('T')


class LocalExperimentCoordinator(Generic[T]):
    def __init__(self, sample_size: int,
                 evaluator: IEvaluator[T],
                 execution_delay_secs: int = 10):
        """
        :param sample_size: the maximum number of individuals to be evaluated per interation
        :param evaluator: an IEvaluator implementation and its method, evaluate_sample,
        will be called when the a sample is ready to be evaluated
        :param execution_delay_secs: max time to wait before running the callback if the sample
         received smaller to the expected
        """
        self._sample_size = sample_size
        self._evaluator = evaluator
        self._local_sample: List[IndividualEntity[T]] = []
        self._exec_delay = execution_delay_secs
        self._is_monitoring = False
        self._iteration_start_time: float | None = None
        self._is_busy = ObservableScalar[bool](False)
        self._is_terminated = ObservableScalar[bool](False)
        self._evaluation_complete_listeners = EventListener[OnEvaluationCompleteCb[T]]()

    @property
    def is_busy(self):
        return self._is_busy

    @property
    def is_terminated(self):
        return self._is_terminated

    @property
    def _is_ready_to_execute(self):
        sample_count = len(self._local_sample)
        return not (self._is_busy.value or sample_count == 0 or not self._iteration_start_time)

    def execute(self):
        if self._is_ready_to_execute:
            self._is_busy.value = True
            Thread(target=self._evaluator.evaluate_sample,
                   args=(self._local_sample, self.__complete_experimentation,),
                   daemon=True
                   ).start()

    def stop(self):
        self._is_terminated.value = True
        self.reset()

    def reset(self):
        # if not self._is_busy.value:
        self._local_sample.clear()
        self._iteration_start_time = None

    def add_untested_individual(self, individual: IndividualEntity[T]):
        if self._is_busy.value:
            return
        if len(self._local_sample) < self._sample_size:
            self._local_sample.append(individual)
            self.__refresh_iteration_start_time()
        if len(self._local_sample) >= self._sample_size:
            self.execute()

    def timeout(self) -> bool:
        if not self._is_ready_to_execute or self._is_busy.value:
            return False
        current_time = time.time()
        time_elapsed = current_time - self._iteration_start_time
        return time_elapsed >= self._exec_delay

    def add_on_evaluation_complete_listener(self, listener: OnEvaluationCompleteCb):
        """
        Listeners are notified when the sample is fully evaluated
        :param listener:
        :return:
        """
        self._evaluation_complete_listeners.add_listener(listener)

    def __complete_experimentation(self, tested_sample: List[IndividualEntity[T]]):
        self.reset()
        self._is_busy.value = False
        self._evaluation_complete_listeners(tested_sample)

    def __refresh_iteration_start_time(self):
        if self._iteration_start_time is None:
            self._iteration_start_time = time.time()
