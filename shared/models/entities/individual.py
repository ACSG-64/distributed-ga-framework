from dataclasses import dataclass
from typing import Generic, TypeVar

from shared.annotations.custom import UUID, FitnessScore

T = TypeVar('T')


@dataclass
class IndividualEntity(Generic[T]):
    id: UUID
    encoding: T
    fitness: FitnessScore | None = None


