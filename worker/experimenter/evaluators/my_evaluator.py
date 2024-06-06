import random
import time
from typing import TypeVar, Generic, List

from shared.models.entities.individual import IndividualEntity
from worker.experimenter.coordinator.implementation import NextCallback

from worker.experimenter.evaluators.interfaces.ievaluator import IEvaluator

T = TypeVar('T')


class MyEvaluator(IEvaluator[T], Generic[T]):
    def __init__(self):
        super().__init__()
        self._counter = 1

    def evaluate_sample(self, sample: List[IndividualEntity[T]], _next: NextCallback[T]) -> None:
        print('Working.....')
        for ind in sample:
            print(ind.id, ind.encoding)
        sample_evaluated = [IndividualEntity[T](id=ind.id, encoding=ind.encoding,
                                                fitness=random.randint(0, 100))
                            for ind in sample]
        print('Results:')
        for ind in sample_evaluated:
            print(ind.id, ind.fitness)
        time.sleep(5)
        print('Done working.....')
        _next(sample_evaluated)
