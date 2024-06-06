from abc import ABC
from typing import TypeVar, Generic

from coordinator.services.messaging.bus.interfaces.imessage_bus import IMessageBus, ResultReceivedListenerCb
from shared.utils.event_listener import EventListener

T = TypeVar('T')


class MessageBusListeners(IMessageBus[T], ABC, Generic[T]):
    def __init__(self):
        self.result_receiver_listeners = EventListener()

    def add_on_result_received_listener(self, listener: ResultReceivedListenerCb):
        self.result_receiver_listeners.add_listener(listener)
        return self
