from abc import ABC

from worker.services.messaging.pubsub.subscriber.interfaces.ipubsub_subscriber import SignalListenerCb
from shared.utils.event_listener import EventListener


class PusSubSubscriberListeners(ABC):
    def __init__(self):
        self.new_generation_listeners = EventListener()
        self.experiment_termination_listeners = EventListener()

    def add_on_new_generation_listener(self, listener: SignalListenerCb):
        self.new_generation_listeners.add_listener(listener)
        return self

    def add_on_experiment_termination_listener(self, listener: SignalListenerCb):
        self.experiment_termination_listeners.add_listener(listener)
        return self
