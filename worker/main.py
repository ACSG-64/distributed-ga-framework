import os
import sys

from dotenv import load_dotenv

from shared.annotations.custom import Genome
from experimenter.coordinator.helpers.runner import LocalCoordinatorRunner
from experimenter.coordinator.implementation import LocalExperimentCoordinator
from experimenter.evaluators.my_evaluator import MyEvaluator
from services.messaging.implementations.rabbitmq.implementation import RabbitMqMessaging

load_dotenv()

AMQP_SERVER_URL = os.getenv('AMQP_SERVER_URL')

messaging = RabbitMqMessaging[Genome](experiment_id=1,
                                      connection_string=AMQP_SERVER_URL)
my_evaluator = MyEvaluator[Genome]()
experiment_coordinator = LocalExperimentCoordinator[Genome](
    sample_size=4, evaluate_sample_callback=my_evaluator.evaluate_sample)

if __name__ == '__main__':
    coordinator_runner = LocalCoordinatorRunner[Genome](experiment_coordinator,
                                                        message_bus=messaging,
                                                        pubsub_sub=messaging)
    coordinator_runner.is_terminated.observe(lambda it_is, _: sys.exit() if it_is else '')
    try:
        coordinator_runner.run()
    except KeyboardInterrupt:
        coordinator_runner.terminate()
