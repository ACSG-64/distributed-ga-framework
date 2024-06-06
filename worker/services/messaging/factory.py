from enum import Enum

from shared.annotations.custom import UUID


class MessageBusDrivers(Enum):
    RABBITMQ = 1


class MessageBusFactory:
    @classmethod
    def create(cls, driver: MessageBusDrivers, experiment_id: UUID, **kwargs):
        if driver == MessageBusDrivers.RABBITMQ:
            #from services.messaging.implementations.rabbitmq.implementation import RabbitMqMessageBus
            return #RabbitMqMessageBus(experiment_id=experiment_id, **kwargs)
        raise Exception
