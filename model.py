from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set


class RideCancelled(Exception):
    pass


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise RideCancelled(f"Out of stock for road {line.road}")


@dataclass(unsafe_hash=True)
class OrderLine:
    rider: str
    road: str
    distance: int


class Batch:
    def __init__(self, ref: str, road: str, distance: int, eta: Optional[date]):
        self.reference = ref
        self.road = road
        self.eta = eta
        self.miles = distance
        self._allocations = set()  # type: Set[OrderLine]

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.distance for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self.miles - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.road == line.road and self.available_quantity >= line.distance
