import _thread
import os
import random

from dotenv import load_dotenv

from experimenter.coordinator.helpers.runner import ExperimentCoordinatorRunner
from experimenter.coordinator.implementation import ExperimentCoordinator
from experimenter.experiments.my_experiment import MyExperiment
from experimenter.helpers.experiment_setup import ExperimentSetupHelper
from services.messaging.implementations.rabbitmq import RabbitMqMessaging
from services.storage.factory import StorageFactory, StorageDrivers
from shared.models.value_objects.individual import IndividualValue
from shared.annotations.custom import Genome

load_dotenv()

AMQP_SERVER_URL = os.getenv('AMQP_SERVER_URL')


def gene_creator(size=3):
    return [random.randint(0, 5) for _ in range(size)]


def individual_creator(genes=3):
    return IndividualValue(encoding=[gene_creator() for _ in range(genes)])


pop = [individual_creator() for i in range(10)]
storage = StorageFactory[Genome].create(driver=StorageDrivers.MEMORY)
ex_id, using_init_pop = ExperimentSetupHelper.setup(experiment_name='ex-1',
                                                    storage=storage,
                                                    initial_population_encodings=pop)
my_experiment = MyExperiment[Genome]()
messaging = RabbitMqMessaging[Genome](experiment_id=ex_id,
                                      connection_string=AMQP_SERVER_URL)
experiment_coordinator = ExperimentCoordinator[Genome](experiment_id=ex_id,
                                                       max_time_between_results_secs=60 * 5,
                                                       storage=storage,
                                                       experiment=my_experiment)

if __name__ == '__main__':
    coordinator_runner = ExperimentCoordinatorRunner[Genome](experiment_coordinator,
                                                             message_bus=messaging,
                                                             pubsub_pub=messaging)
    coordinator_runner.is_terminated.observe(lambda it_is, _:
                                             _thread.interrupt_main() if it_is else '')
    try:
        coordinator_runner.run(should_await=not using_init_pop)
    except KeyboardInterrupt:
        coordinator_runner.terminate()
