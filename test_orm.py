import model
from datetime import date

from sqlalchemy import select, delete
from sqlalchemy.sql import text


def test_orderline_mapper_can_load_lines(session):
    # delete all records first
    session.execute(delete(model.OrderLine))

    session.execute(
        text(
            "INSERT INTO order_lines (rider, road, distance) VALUES "
            '("James", "HWY1863", 12),'
            '("James", "HWY46", 13),'
            '("Steve", "BlueCreekRd", 14)'
        )
    )
    expected = [
        model.OrderLine("James", "HWY1863", 12),
        model.OrderLine("James", "HWY46", 13),
        model.OrderLine("Steve", "BlueCreekRd", 14),
    ]
    # assert session.query(model.OrderLine).all() == expected
    outcome = session.scalars(select(model.OrderLine)).all()
    print(outcome)
    assert outcome == expected
    session.close()


def test_orderline_mapper_can_save_lines(session):
    # delete all records first
    session.execute(delete(model.OrderLine))

    new_line = model.OrderLine("James", "RiverRd", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(text('SELECT rider, road, distance FROM "order_lines"')))
    assert rows == [("James", "RiverRd", 12)]

    session.close()


def test_retrieving_batches(session):
    # delete all records first
    session.execute(delete(model.Ride))
    session.execute(
        text(
            "INSERT INTO rides (reference, road, miles, eta)"
            ' VALUES ("ride1", "road1", 100, null)'
        )
    )
    session.execute(
        text(
            "INSERT INTO rides (reference, road, miles, eta)"
            ' VALUES ("ride2", "road2", 200, "2011-04-11")'
        )
    )
    expected = [
        model.Ride("ride1", "road1", 100, eta=None),
        model.Ride("ride2", "road2", 200, eta=date(2011, 4, 11)),
    ]

    assert session.query(model.Ride).all() == expected

    session.close()


def test_saving_batches(session):
    # delete all records first
    session.execute(delete(model.Ride))
    ride = model.Ride("ride1", "road1", 100, eta=None)
    session.add(ride)
    session.commit()
    rows = session.execute(
        text('SELECT reference, road, miles, eta FROM "rides"')
    )
    assert list(rows) == [("ride1", "road1", 100, None)]

    session.close()


def test_saving_allocations(session):
    # delete all records first
    session.execute(delete(model.Ride))
    session.execute(delete(model.OrderLine))
    ride = model.Ride("ride1", "road1", 100, eta=None)
    route = model.OrderLine("James", "road1", 10)
    ride.allocate(route)
    session.add(ride)
    session.commit()
    rows = list(
        session.execute(
            text('SELECT orderline_id, batch_id FROM "allocations"')
        ).first()
    )
    assert rows == [ride.id, route.id]

    session.close()


def test_retrieving_allocations(session):
    # delete all records first
    session.execute(delete(model.Ride))
    session.execute(delete(model.OrderLine))
    session.execute(
        text(
            'INSERT INTO order_lines (rider, road, distance) VALUES ("James", "road1", 12)'
        )
    )
    [[olid]] = session.execute(
        text("SELECT id FROM order_lines WHERE rider=:rider AND road=:road"),
        dict(rider="James", road="road1"),
    )
    session.execute(
        text(
            "INSERT INTO rides (reference, road, miles, eta)"
            ' VALUES ("ride1", "road1", 100, null)'
        )
    )
    [[bid]] = session.execute(
        text("SELECT id FROM rides WHERE reference=:ref AND road=:road"),
        dict(ref="ride1", road="road1"),
    )
    session.execute(
        text("INSERT INTO allocations (orderline_id, batch_id) VALUES (:olid, :bid)"),
        dict(olid=olid, bid=bid),
    )

    ride = session.query(model.Ride).one()

    assert ride._allocations == {model.OrderLine("James", "road1", 12)}

    session.close()
