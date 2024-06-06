import json
from typing import TypeVar, Generic, Tuple

from shared.annotations.custom import UUID, FitnessScore
from coordinator.services.messaging.bus.abstract.message_bus_listeners import MessageBusListeners
from coordinator.services.messaging.bus.interfaces.imessage_bus import IMessageBus
from coordinator.services.messaging.pubsub.publisher.interfaces.ipubsub_publisher import IPubSubPublisher
from shared.services.messaging.implementations.rabbitmq import RabbitMqMessagingBaseControls
from shared.utils.promise import Promise

T = TypeVar('T')


class RabbitMqMessaging(RabbitMqMessagingBaseControls,
                        MessageBusListeners[T],
                        IMessageBus[T], IPubSubPublisher,
                        Generic[T]):
    """
    An AMQP 0-9-1 implementation of both Messaging Queue and PubSub Publisher
    """
    def __init__(self, connection_string: str, experiment_id: UUID):
        RabbitMqMessagingBaseControls.__init__(self, connection_string, experiment_id)
        MessageBusListeners.__init__(self)
        self.ex_id = experiment_id

    @property
    def pending_deliveries_count(self) -> Promise[int]:
        promise = Promise[int]()
        resolve, reject = promise.handlers
        try:
            self.channel.queue_declare(queue=self.individuals_q, passive=True,
                                       callback=lambda frame: resolve(frame.method.message_count))
        except Exception as e:
            reject(e)
        return promise

    def send_individual(self, individual_id: UUID, encoding: T):
        msg = {'id': individual_id, 'encoding': encoding}
        msg_json = json.dumps(msg)
        self.channel.basic_publish(exchange='',
                                   routing_key=self.individuals_q,
                                   body=msg_json)

    def clear_individuals_queue(self):
        self.channel.queue_purge(queue=self.individuals_q)

    def broadcast_new_generation_signal(self):
        self.channel.basic_publish(exchange=self.new_gen_ex, routing_key='',
                                   body='NEW GENERATION INCOMING')

    def broadcast_experiment_termination_signal(self):
        print('Broadcasting')
        self.channel.basic_publish(exchange=self.termination_ex, routing_key='',
                                   body='EXPERIMENT TERMINATED')

    def on_channel_open(self, channel):
        self.channel = channel
        # Setup exchanges (pub/sub)
        channel.exchange_declare(exchange=self.new_gen_ex,
                                 exchange_type='fanout')
        channel.exchange_declare(exchange=self.termination_ex,
                                 exchange_type='fanout')
        # Setup queues
        channel.queue_declare(queue=self.individuals_q,
                              callback=self._acknowledge_queue_declaration)
        channel.queue_declare(queue=self.results_q,
                              callback=self._acknowledge_queue_declaration)
        channel.basic_consume(queue=self.results_q,
                              on_message_callback=self.__on_result_received_msg)
        self._start_keep_alive_thread()  # prepare thread
        self.is_starting_up = False  # fully ready
        print('MAIN', self.is_listening)
        if self._is_fully_initialized:
            self._call_start_callback()

    def __on_result_received_msg(self, channel, method, _, body):
        res = self.__message_parser(body)
        if res:
            self.result_receiver_listeners(res[0], res[1])
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_nack(delivery_tag=method.delivery_tag)

    @staticmethod
    def __message_parser(raw_msg: str | bytes | bytearray) -> Tuple[UUID, FitnessScore] | None:
        try:
            msg = json.loads(raw_msg)
        except TypeError:
            return None
        if 'id' not in msg or 'fitness' not in msg:
            return None
        return msg['id'], msg['fitness']
