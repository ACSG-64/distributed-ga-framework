from abc import ABC
from typing import TypeVar, Generic

from worker.services.messaging.bus.interfaces.imessage_bus import IndividualReceivedListenerCb, IMessageBus
from shared.utils.event_listener import EventListener

T = TypeVar('T')


class MessageBusListeners(IMessageBus[T], ABC, Generic[T]):
    def __init__(self):
        self.individual_received_listeners = EventListener()

    def add_on_individual_received_listener(self, listener: IndividualReceivedListenerCb[T]):
        self.individual_received_listeners.add_listener(listener)
        return self
