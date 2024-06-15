import os
import sys

from dotenv import load_dotenv

from shared.annotations.custom import Genome
from worker.experimenter.coordinator.helpers.runner import LocalCoordinatorRunner
from worker.experimenter.coordinator.implementation import LocalExperimentCoordinator
from worker.experimenter.evaluators.my_evaluator import MyEvaluator
from worker.helpers.setup_settings_prompt import setup_settings_prompt
from worker.services.messaging.implementations.rabbitmq.implementation import RabbitMqMessaging


def main():
    print('[[WORKER]]')
    load_dotenv()
    AMQP_SERVER_URL = os.getenv('AMQP_SERVER_URL')
    EX_ID, SAMPLE_SIZE = setup_settings_prompt()

    messaging = RabbitMqMessaging[Genome](experiment_id=EX_ID,
                                          connection_string=AMQP_SERVER_URL)
    my_evaluator = MyEvaluator[Genome]()
    experiment_coordinator = LocalExperimentCoordinator[Genome](sample_size=SAMPLE_SIZE,
                                                                evaluator=my_evaluator)

    coordinator_runner = LocalCoordinatorRunner[Genome](experiment_coordinator,
                                                        message_bus=messaging,
                                                        pubsub_sub=messaging)
    coordinator_runner.is_terminated.observe(lambda it_is, _: sys.exit() if it_is else '')
    try:
        coordinator_runner.run()
    except KeyboardInterrupt:
        coordinator_runner.terminate()


if __name__ == '__main__':
    main()
