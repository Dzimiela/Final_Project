from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set


class RideCancelled(Exception):
    pass


def allocate(route: NewRoute, rides: List[Ride]) -> str:
    try:
        ride = next(b for b in sorted(rides) if b.can_allocate(route))
        ride.allocate(route)
        return ride.reference
    except StopIteration:
        raise RideCancelled(f"Ride tommorow {route.road}")


@dataclass(unsafe_hash=True)
class NewRoute:
    rider: str
    road: str
    distance: int
   

class Ride:
    def __init__(self, ref: str, road: str, distance: int, speed: int, eta: Optional[date]):
        self.reference = ref
        self.road = road
        self.eta = eta
        self.miles = distance
        self.mph = speed
        self._allocations = set()  # type: Set[NewRoute]

    def __repr__(self):
        return f"<Ride {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Ride):
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

    def allocate(self, route: NewRoute):
        if self.can_allocate(route):
            self._allocations.add(route)

    def deallocate(self, route: NewRoute):
        if route in self._allocations:
            self._allocations.remove(route)

    @property
    def allocated_quantity(self) -> int:
        return sum(route.distance for route in self._allocations)

    @property
    def total_miles(self) -> int:
        return self.miles - self.allocated_quantity
    
    @property
    def speed_mph(self) -> int:
        return self.mph - self.allocated_quantity

    def can_allocate(self, route: NewRoute) -> bool:
        return self.road == route.road and self.total_miles >= route.distance
