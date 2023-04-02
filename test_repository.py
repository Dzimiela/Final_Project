# pylint: disable=protected-access
import model
import repository

from sqlalchemy import select, delete
from sqlalchemy.sql import text


def test_repository_can_save_a_batch(session):
    # delete all records first
    session.execute(delete(model.Ride))
    session.execute(delete(model.OrderLine))
    ride = model.Ride("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(ride)
    session.commit()

    rows = session.execute(
        text('SELECT reference, road, miles, eta FROM "batches"')
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]

    session.commit()


def insert_order_line(session):
    session.execute(
        text(
            "INSERT INTO order_lines (rider, road, distance)"
            ' VALUES ("James", "GENERIC-SOFA", 12)'
        )
    )
    [[orderline_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE rider=:rider AND road=:road"),
        dict(rider="James", road="GENERIC-SOFA"),
    )
    return orderline_id


def insert_batch(session, batch_id):
    session.execute(
        text(
            "INSERT INTO batches (reference, road, miles, eta)"
            ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)',
        ),
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        text('SELECT id FROM batches WHERE reference=:batch_id AND road="GENERIC-SOFA"'),
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
    session.execute(delete(model.OrderLine))
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Ride("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Ride.__eq__ only compares reference
    assert retrieved.road == expected.road
    assert retrieved.miles == expected.miles
    assert retrieved._allocations == {
        model.OrderLine("James", "GENERIC-SOFA", 12),
    }
