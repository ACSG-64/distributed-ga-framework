from abc import abstractmethod

from shared.services.messaging.pubsub.interfaces.ipubsub import IPubSubControls


class IPubSubPublisher(IPubSubControls):
    @abstractmethod
    def broadcast_new_generation_signal(self):
        raise NotImplementedError

    @abstractmethod
    def broadcast_experiment_termination_signal(self):
        raise NotImplementedError
