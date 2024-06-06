from abc import ABC, abstractmethod
from typing import Generic, TypeVar, TypeAlias, Callable

from shared.annotations.custom import UUID, FitnessScore
from shared.services.messaging.bus.interfaces.imessage_bus import IMessageBusControls
from shared.utils.promise import Promise

T = TypeVar('T')

ResultReceivedListenerCb: TypeAlias = Callable[[UUID, FitnessScore], any]


class IMessageBus(IMessageBusControls, ABC, Generic[T]):
    @property
    @abstractmethod
    def pending_deliveries_count(self) -> Promise[int]:
        raise NotImplementedError

    @abstractmethod
    def send_individual(self, individual_id: UUID, encoding: T):
        raise NotImplementedError

    @abstractmethod
    def clear_individuals_queue(self):
        raise NotImplementedError

    @abstractmethod
    def add_on_result_received_listener(self, listener: ResultReceivedListenerCb):
        return self
