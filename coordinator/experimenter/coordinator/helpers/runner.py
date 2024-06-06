import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Thread, Event
from typing import TypeVar, Generic, List

from shared.annotations.custom import UUID, FitnessScore
from coordinator.experimenter.coordinator.implementation import ExperimentCoordinator
from shared.models.entities.individual import IndividualEntity
from coordinator.services.messaging.bus.interfaces.imessage_bus import IMessageBus
from coordinator.services.messaging.pubsub.publisher.interfaces.ipubsub_publisher import IPubSubPublisher
from shared.utils.observable_scalar import ObservableScalar
from shared.utils.promise import PromiseStatus

T = TypeVar('T')


def safe_pause_coordinator_thread(fn):
    def action(self, *args, **kwargs):
        self.stop_threaded_monitor()
        res = fn(self, *args, **kwargs)
        self.start_threaded_monitor()
        return res

    return action


class ExperimentCoordinatorRunner(Generic[T]):
    def __init__(self, experiment_coordinator: ExperimentCoordinator,
                 message_bus: IMessageBus, pubsub_pub: IPubSubPublisher,
                 monitor_interval_secs=5.0):
        self.experiment_coordinator = experiment_coordinator
        self.message_bus: IMessageBus = message_bus
        self.pubsub_pub: IPubSubPublisher = pubsub_pub
        self.monitor_interval_secs = monitor_interval_secs
        self.stop_event = Event()
        self.monitor_thread: Thread = Thread()
        self._is_terminated = ObservableScalar[bool](False)
        self.__setup_listeners()

    @property
    def is_terminated(self):
        return self._is_terminated

    def run(self, should_await=False):
        callback = partial(self.__start, should_await)
        if self.message_bus == self.pubsub_pub:
            self.message_bus.listen(callback)
            return
        with ThreadPoolExecutor() as executor:
            executor.submit(self.message_bus.listen, callback)
            executor.submit(self.pubsub_pub.listen)

    def terminate(self):
        self.stop_threaded_monitor()
        try:
            self.pubsub_pub.broadcast_experiment_termination_signal()
            time.sleep(5)
            self.__stop_messaging_services()
        except:
            pass
        finally:
            self._is_terminated.value = True

    def start_threaded_monitor(self):
        self.stop_threaded_monitor()
        self.stop_event.clear()
        self.monitor_thread = Thread(target=self.__monitor, daemon=True)
        self.monitor_thread.start()

    def stop_threaded_monitor(self):
        self.stop_event.set()
        if self.monitor_thread.is_alive():
            self.monitor_thread.join()

    def __setup_listeners(self):
        experiment_coordinator = self.experiment_coordinator
        message_bus = self.message_bus
        # Observers
        experiment_coordinator.is_terminated \
            .observe(lambda it_is, _: self.terminate() if it_is else '')
        # Events
        experiment_coordinator \
            .add_on_population_evaluated_listener(lambda _: self.message_bus
                                                  .clear_individuals_queue) \
            .add_on_testing_sample_selected_listener(lambda _: self.pubsub_pub
                                                     .broadcast_new_generation_signal()) \
            .add_on_testing_sample_selected_listener(self.__send_testing_sample)
        message_bus.add_on_result_received_listener(self.__add_result)

    def __stop_messaging_services(self):
        self.message_bus.stop()
        if self.message_bus != self.pubsub_pub:
            self.pubsub_pub.stop()

    def __start(self, _await: bool):
        if not _await:
            pending_ind = self.experiment_coordinator.untested_individuals
            self.pubsub_pub.broadcast_new_generation_signal()
            self.__send_testing_sample(pending_ind)
        self.start_threaded_monitor()

    @safe_pause_coordinator_thread
    def __add_result(self, _id: UUID, fitness: FitnessScore):
        self.experiment_coordinator.add_individual_fitness(_id, fitness)

    def __send_testing_sample(self, sample: List[IndividualEntity]):
        for ind in sample:
            self.message_bus.send_individual(ind.id, ind.encoding)

    def __monitor(self):
        message_bus = self.message_bus
        msgs_count_promise = None
        while not self.stop_event.is_set():
            self.stop_event.wait(self.monitor_interval_secs)
            if (msgs_count_promise and
                    msgs_count_promise.status != PromiseStatus.FULFILLED):
                continue
            msgs_count_promise = message_bus.pending_deliveries_count
            msgs_count_promise \
                .then(self.__resend_sample_on_timeout) \
                .catch(lambda e: '') # TODO handle it

    def __resend_sample_on_timeout(self, pending_msgs_count: int):
        experiment_coordinator = self.experiment_coordinator
        if experiment_coordinator.timeout(pending_msgs_count):
            testing_sample = experiment_coordinator.untested_individuals
            self.__send_testing_sample(testing_sample)
