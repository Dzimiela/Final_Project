# pylint: disable=redefined-outer-name
import time
from pathlib import Path

import pytest
import requests
from requests.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.sql import delete, insert, select, text
from sqlalchemy.orm import sessionmaker, clear_mappers

import config
from flask_app import create_app
from model import Ride
from orm import mapper_registry, start_mappers, rides


# chapter reworked to follow
# https://flask.palletsprojects.com/en/2.2.x/patterns/appfactories/#application-factories
# and
# https://flask.palletsprojects.com/en/2.2.x/testing/#testing-flask-applications
# P&G might be too fixated on Docker containers with their example.


@pytest.fixture
def in_memory_db():
    engine = create_engine(f"sqlite:///:memory:")
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture
def file_sqlite_db():
    engine = create_engine(config.get_sqlite_filedb_uri())
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(file_sqlite_db):
    start_mappers()
    yield sessionmaker(bind=file_sqlite_db)()
    clear_mappers()


@pytest.fixture
def flask_api(session):
    app = create_app()
    app.config.update({"Route Test": True})
    return app


@pytest.fixture
def test_client(flask_api):
    return flask_api.test_client()


@pytest.fixture
def add_stock(session):
    # take care and note that this fixture takes care of adding in records to the database.
    batches_added = set()
    roads_added = set()

    def _add_stock(lines):
        print(lines)
        for ref, road, distance, eta in lines:
            session.execute(
                insert(rides).values(
                    reference=ref, road=road, miles=distance, eta=eta
                )
            )
            batch_id = session.scalars(
                select(Ride).where(Ride.reference == ref).where(Ride.road == road)
            ).first()
            print(batch_id.reference)
            print(batch_id.road)
            batches_added.add(batch_id.reference)
            roads_added.add(batch_id.road)
        session.commit()
        session.close()

    yield _add_stock

    for batch_id in batches_added:
        session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            dict(batch_id=batch_id),
        )
        session.execute(
            text("DELETE FROM rides WHERE id=:batch_id"),
            dict(batch_id=batch_id),
        )
    for road in roads_added:
        session.execute(
            text("DELETE FROM order_lines WHERE road=:road"),
            dict(road=road),
        )

    session.commit()
