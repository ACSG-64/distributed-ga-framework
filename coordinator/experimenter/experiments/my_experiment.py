import random
from typing import List, TypeVar, Generic

from shared.models.entities.individual import IndividualEntity
from coordinator.experimenter.coordinator.implementation import NextCallback, StopCallback
from coordinator.experimenter.experiments.interfaces.iexperiment import IExperiment
from shared.models.value_objects.individual import IndividualValue

T = TypeVar('T')


def gene_creator(size=3):
    return [random.randint(0, 5) for _ in range(size)]


def individual_creator(genes=3):
    return IndividualValue(encoding=[gene_creator() for _ in range(genes)])


class MyExperiment(IExperiment, Generic[T]):
    def __init__(self):
        super().__init__()
        self._counter = 1

    def apply_genetic_operations(self, population: List[IndividualEntity[T]],
                                 _next: NextCallback[T], _stop: StopCallback) -> None:
        print(f'Population of {len(population)} individuals')
        for individual in population:
            print(f'Stats: {individual.id} - {individual.fitness}')
        if self._counter >= 2:
            return _stop()
        new_pop = [individual_creator() for _ in range(10 - 3)]
        new_pop.extend([IndividualValue(encoding=ind.encoding, fitness=ind.fitness)
                        for ind in population[:3]])

        print('Last new pop last three')
        for individual in new_pop[:3]:
            print(individual.fitness)
        self._counter += 1
        _next(new_pop)
