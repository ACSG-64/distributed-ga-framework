from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread, Event
from typing import TypeVar, Generic, List

from shared.annotations.custom import UUID
from shared.models.entities.individual import IndividualEntity
from shared.utils.thread_safe import global_thread_safe
from worker.experimenter.coordinator.implementation import LocalExperimentCoordinator
from worker.services.messaging.bus.interfaces.imessage_bus import IMessageBus
from worker.services.messaging.pubsub.subscriber.interfaces.ipubsub_subscriber import IPubSubSubscriber
from shared.utils.observable_scalar import ObservableScalar

T = TypeVar('T')


def safe_pause_coordinator_thread(fn):
    def action(self, *args, **kwargs):
        self.stop_threaded_monitor()
        res = fn(self, *args, **kwargs)
        self.start_threaded_monitor()
        return res

    return action


class LocalCoordinatorRunner(Generic[T]):
    def __init__(self, experiment_coordinator: LocalExperimentCoordinator,
                 message_bus: IMessageBus, pubsub_sub: IPubSubSubscriber):
        self.experiment_coordinator = experiment_coordinator
        self.message_bus: IMessageBus = message_bus
        self.pubsub_sub: IPubSubSubscriber = pubsub_sub
        self.stop_event = Event()
        self.monitor_thread: Thread = Thread()
        self._is_terminated = ObservableScalar[bool](False)
        self.__setup_listeners()
        self._execution_signal_q = Queue()

    @property
    def is_terminated(self):
        return self._is_terminated

    @global_thread_safe
    def run(self):
        if self.message_bus == self.pubsub_sub:
            self.message_bus.listen(callback=self.start_threaded_monitor)
            return
        with ThreadPoolExecutor() as executor:
            executor.submit(self.message_bus.listen, callback=self.start_threaded_monitor)
            executor.submit(self.pubsub_sub.listen)

    @global_thread_safe
    def terminate(self):
        self.stop_threaded_monitor()
        self.__stop_messaging_services()
        self._is_terminated.value = True

    @global_thread_safe
    def start_threaded_monitor(self):
        self.stop_threaded_monitor()
        self.stop_event.clear()
        self.monitor_thread = Thread(target=self.__monitor, daemon=True)
        self.monitor_thread.start()

    @global_thread_safe
    def stop_threaded_monitor(self):
        self.stop_event.set()
        if self.monitor_thread.is_alive():
            self.monitor_thread.join()

    @global_thread_safe
    def __setup_listeners(self):
        experiment_coordinator = self.experiment_coordinator
        message_bus = self.message_bus
        pubsub_sub = self.pubsub_sub

        experiment_coordinator.is_terminated \
            .observe(lambda it_is, _: self.terminate() if it_is else '')

        experiment_coordinator.is_busy \
            .observe(lambda it_is, _: message_bus.pause() if it_is else message_bus.resume())
        experiment_coordinator.add_on_evaluation_complete_listener(self.__send_tested_sample)

        message_bus \
            .add_on_individual_received_listener(self.__add_incoming_individual)
        pubsub_sub \
            .add_on_new_generation_listener(experiment_coordinator.reset) \
            .add_on_experiment_termination_listener(experiment_coordinator.stop)

    @global_thread_safe
    def __stop_messaging_services(self):
        self.message_bus.stop()
        if self.message_bus != self.pubsub_sub:
            self.pubsub_sub.stop()

    @global_thread_safe
    @safe_pause_coordinator_thread
    def __add_incoming_individual(self, _id: UUID, encoding: T):
        individual = IndividualEntity(_id, encoding)
        self.experiment_coordinator.add_untested_individual(individual)

    @global_thread_safe
    def __send_tested_sample(self, sample: List[IndividualEntity]):
        for ind in sample:
            self.message_bus.send_result(ind.id, ind.fitness)

    @global_thread_safe
    def __monitor(self):
        stop_event = self.stop_event
        while not stop_event.is_set():
            if self.experiment_coordinator.timeout():
                self.experiment_coordinator.execute()
            stop_event.wait(5)
