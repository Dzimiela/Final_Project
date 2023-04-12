# pylint: disable=protected-access
import model
import repository

from sqlalchemy import select, delete
from sqlalchemy.sql import text


def test_repository_can_save_a_batch(session):
    # delete all records first
    session.execute(delete(model.Ride))
    session.execute(delete(model.NewRoute))
    ride = model.Ride("ride1", "DogSquatRoad", 40, 18, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(ride)
    session.commit()

    rows = session.execute(
        text('SELECT reference, road, miles, mph, eta FROM "rides"')
    )
    assert list(rows) == [("ride1", "DogSquatRoad", 40, 18, None)]

    session.commit()


def insert_order_line(session):
    session.execute(
        text(
            "INSERT INTO new_routes (rider, road, distance, mph)"
            ' VALUES ("James", "HairyCatRoad", 20, 12)'
        )
    )
    [[orderline_id]] = session.execute(
        text("SELECT id FROM new_routes WHERE rider=:rider AND road=:road"),
        dict(rider="James", road="HairyCatRoad"),
    )
    return orderline_id


def insert_batch(session, batch_id):
    session.execute(
        text(
            "INSERT INTO rides (reference, road, miles, eta)"
            ' VALUES (:batch_id, "HairyCatRoad", 40, null)',
        ),
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        text('SELECT id FROM rides WHERE reference=:batch_id AND road="HairyCatRoad"'),
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        text(
            "INSERT INTO allocations (orderline_id, batch_id)"
            " VALUES (:orderline_id, :batch_id)"
        ),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(session):
    # delete all records first
    session.execute(delete(model.Ride))
    session.execute(delete(model.NewRoute))
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "ride1")
    insert_batch(session, "ride2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("ride1")

    expected = model.Ride("ride1", "HairyCatRoad", 40, 16, eta=None)
    assert retrieved == expected  # Ride.__eq__ only compares reference
    assert retrieved.road == expected.road
    assert retrieved.miles == expected.miles
    assert retrieved._allocations == {
        model.NewRoute("James", "HairyCatRoad", 12, 15),
    }
