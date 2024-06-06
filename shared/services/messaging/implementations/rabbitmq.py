from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Thread, Event
from typing import Callable, List

import pika

from shared.annotations.custom import UUID
from shared.services.messaging.bus.interfaces.imessage_bus import IMessageBusControls
from shared.services.messaging.pubsub.interfaces.ipubsub import IPubSubControls


@dataclass
class PausableQueue:
    consumer_tag: str
    basic_consume_params: dict


class RabbitMqMessagingBaseControls(IMessageBusControls, IPubSubControls, ABC):
    def __init__(self, connection_string: str, experiment_id: UUID, total_queues: int = 0):
        ex_prefix = f'ex-{experiment_id}'
        self.individuals_q = f'{ex_prefix}-individuals'
        self.results_q = f'{ex_prefix}-results'
        self.new_gen_ex = f'{ex_prefix}-new-generation-signal'
        self.termination_ex = f'{ex_prefix}-termination-signal'
        self.pausable_queues: List[PausableQueue] = []
        # Setup implementations
        self.params = pika.URLParameters(connection_string)
        self.connection = None
        self.channel = None
        # Status
        self.is_starting_up = False
        self._is_stopped = False
        self._start_cb: Callable[[], any] | None = None
        self._keep_alive_thread = Thread()
        self._stop_event = Event()
        self._queue_count = total_queues
        self._queue_declared_count = 0

    @abstractmethod
    def on_channel_open(self, channel):  # protected method
        """
        This is a protected method.
        Here should be placed the queues, exchanges and so on declaration and initialization
        :param channel: a Pika channel created by a SelectConnection
        """
        raise NotImplementedError

    @property
    def is_listening(self) -> bool:
        return self.channel and self.channel.is_open

    @property
    def is_stopped(self) -> bool:
        return self._is_stopped

    @property
    def _is_fully_initialized(self) -> bool:
        return (self._queue_declared_count >= self._queue_count
                and not self.is_starting_up)

    def listen(self, callback: Callable[[], any] | None = None):
        if self.is_listening or self.is_starting_up:
            return
        self.is_starting_up = True  # starting but not ready
        self._is_stopped = False
        self._start_cb = callback
        self.connection = pika.SelectConnection(parameters=self.params,
                                                on_open_callback=self.__on_open,
                                                on_close_callback=self.__on_close)
        self.connection.ioloop.start()

    def pause(self):
        if not self.channel:
            return
        for pq in self.pausable_queues:
            self.channel.basic_cancel(consumer_tag=pq.consumer_tag)

    def resume(self):
        if not self.channel:
            return
        for pq in self.pausable_queues:
            pq.consumer_tag = self.channel.basic_consume(**pq.basic_consume_params)

    def stop(self):
        if not self._is_stopped:
            self._is_stopped = True
            self.connection.close()

    def _start_keep_alive_thread(self):
        """
        Starts the function in background as a daemon thread
        :return:
        """
        self._stop_event.clear()
        self._keep_alive_thread = Thread(target=self.__keep_alive, daemon=True)
        self._keep_alive_thread.start()

    def __on_open(self, connection):
        connection.channel(on_open_callback=self.on_channel_open)

    def _acknowledge_queue_declaration(self, _):
        self._queue_declared_count += 1
        if self._is_fully_initialized:
            self._call_start_callback()

    def _call_start_callback(self):
        if self._start_cb:
            self._start_cb()
            self._start_cb = None

    def __on_close(self, a, b):
        self._stop_event.set()  # stops the thread
        if self._keep_alive_thread.is_alive():
            self._keep_alive_thread.join()  # wait until it finishes

    def __keep_alive(self):
        """
        Periodically makes a request to the server to avoid being offline due to inactivity
        """
        while not self._stop_event.is_set():
            self.channel.queue_declare(queue=self.individuals_q, passive=True)
            self._stop_event.wait(15)
