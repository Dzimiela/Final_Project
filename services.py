from __future__ import annotations

import model
from model import OrderLine
from repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_road(road, batches):
    return road in {b.road for b in batches}


def allocate(route: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_road(route.road, batches):
        raise InvalidSku(f"Invalid road {route.road}")
    batchref = model.allocate(route, batches)
    session.commit()
    return batchref
