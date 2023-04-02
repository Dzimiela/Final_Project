from __future__ import annotations

import model
from model import NewRoute
from repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_road(road, rides):
    return road in {b.road for b in rides}


def allocate(route: NewRoute, repo: AbstractRepository, session) -> str:
    rides = repo.list()
    if not is_valid_road(route.road, rides):
        raise InvalidSku(f"Invalid road {route.road}")
    batchref = model.allocate(route, rides)
    session.commit()
    return batchref
