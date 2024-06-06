from abc import ABC, abstractmethod
from typing import Callable, TypeAlias

from shared.services.messaging.pubsub.interfaces.ipubsub import IPubSubControls

SignalListenerCb: TypeAlias = Callable[[], any]


class IPubSubSubscriber(IPubSubControls, ABC):
    @abstractmethod
    def add_on_new_generation_listener(self, listener: SignalListenerCb):
        return self

    @abstractmethod
    def add_on_experiment_termination_listener(self, listener: SignalListenerCb):
        return self
