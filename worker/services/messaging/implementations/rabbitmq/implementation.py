import json
import time
from typing import TypeVar, Generic, Tuple

from shared.annotations.custom import UUID, FitnessScore
from worker.services.messaging.bus.abstract.message_bus_listeners import MessageBusListeners
from worker.services.messaging.bus.interfaces.imessage_bus import IMessageBus
from worker.services.messaging.implementations.rabbitmq.utils.setup_queues import create_temporal_exchange_queue
from worker.services.messaging.pubsub.subscriber.abstract.pubsub_subscriber_listeners import PusSubSubscriberListeners
from worker.services.messaging.pubsub.subscriber.interfaces.ipubsub_subscriber import IPubSubSubscriber
from shared.services.messaging.implementations.rabbitmq import RabbitMqMessagingBaseControls, PausableQueue

T = TypeVar('T')

COUNT = 0


class RabbitMqMessaging(RabbitMqMessagingBaseControls,
                        MessageBusListeners[T], PusSubSubscriberListeners,
                        IMessageBus[T], IPubSubSubscriber,
                        Generic[T]):

    def __init__(self, connection_string: str, experiment_id: UUID):
        RabbitMqMessagingBaseControls.__init__(self, connection_string, experiment_id)
        MessageBusListeners.__init__(self)
        PusSubSubscriberListeners.__init__(self)
        self.ex_id = experiment_id

    def send_result(self, individual_id: UUID, fitness: FitnessScore):
        msg = {'id': individual_id, 'fitness': fitness}
        msg_json = json.dumps(msg)
        self.channel.basic_publish(exchange='', body=msg_json,
                                   routing_key=self.results_q)

    def on_channel_open(self, channel):
        self.channel = channel
        # Consume one message at a time
        channel.basic_qos(prefetch_count=1, callback=lambda _: self.__setup_queues(channel))
        # Setup exchanges
        # new generation signal
        channel.exchange_declare(exchange=self.new_gen_ex,
                                 exchange_type='fanout')
        # experiment termination signal
        channel.exchange_declare(exchange=self.termination_ex,
                                 exchange_type='fanout')

    def __setup_queues(self, channel):
        # Setup queues
        channel.queue_declare(queue=self.results_q)
        channel.queue_declare(queue=self.individuals_q)
        ind_q_bc_params = {
            'queue': self.individuals_q,
            'on_message_callback': self.__on_individual_received_msg
        }
        c_tag = channel.basic_consume(**ind_q_bc_params)
        self.pausable_queues.append(PausableQueue(consumer_tag=c_tag,
                                                  basic_consume_params=ind_q_bc_params))
        # setup temporal, exclusive receiver queues for exchanges
        create_temporal_exchange_queue(channel, exchange_name=self.new_gen_ex) \
            .then(lambda q_name: channel
                  .basic_consume(queue=q_name,
                                 on_message_callback=self.__on_new_generation_signal_msg))
        create_temporal_exchange_queue(channel, exchange_name=self.termination_ex) \
            .then(lambda q_name: channel.
                  basic_consume(queue=q_name,
                                on_message_callback=self.__on_experiment_termination_signal_msg))
        self._start_keep_alive_thread()  # prepare thread
        self.is_starting_up = False  # fully ready
        if self._is_fully_initialized:
            self._call_start_callback()

    def __on_individual_received_msg(self, channel, method, _, body):
        ind = self.__message_parser(body)
        if ind:
            self.individual_received_listeners(ind[0], ind[1])
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_nack(delivery_tag=method.delivery_tag)

    def __on_new_generation_signal_msg(self, channel, method, _, __):
        channel.basic_ack(delivery_tag=method.delivery_tag)
        self.new_generation_listeners()

    def __on_experiment_termination_signal_msg(self, channel, method, _, __):
        self.experiment_termination_listeners()
        channel.basic_ack(delivery_tag=method.delivery_tag)

    @staticmethod
    def __message_parser(raw_msg: str | bytes | bytearray) -> Tuple[UUID, T] | None:
        try:
            msg = json.loads(raw_msg)
        except TypeError:
            return None
        if 'id' not in msg or 'encoding' not in msg:
            return None
        return msg['id'], msg['encoding']
