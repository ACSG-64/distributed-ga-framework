from abc import ABC, abstractmethod
from typing import Generic, Callable, TypeVar, TypeAlias

from shared.annotations.custom import UUID, FitnessScore
from shared.services.messaging.bus.interfaces.imessage_bus import IMessageBusControls

T = TypeVar('T')

IndividualReceivedListenerCb: TypeAlias = Callable[[UUID, T], any]
SignalListenerCb: TypeAlias = Callable[[], any]


class IMessageBus(IMessageBusControls, ABC, Generic[T]):
    @abstractmethod
    def send_result(self, individual_id: UUID, fitness: FitnessScore):
        raise NotImplementedError

    @abstractmethod
    def add_on_individual_received_listener(self, listener: IndividualReceivedListenerCb[T]):
        return self
