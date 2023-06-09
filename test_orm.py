import model
from datetime import date

from sqlalchemy import select, delete
from sqlalchemy.sql import text


def test_orderline_mapper_can_load_lines(session):
    # delete all records first
    session.execute(delete(model.NewRoute))

    session.execute(
        text(
            "INSERT INTO new_routes (rider, road, distance, mph) VALUES "
            '("James", "HWY1863", 21),'
            '("James", "HWY46", 20),'
            '("Steve", "BlueCreekRd", 18)'
        )
    )
    expected = [
        model.NewRoute("James", "HWY1863", 21),
        model.NewRoute("James", "HWY46", 20),
        model.NewRoute("Steve", "BlueCreekRd", 18),
    ]
    # assert session.query(model.NewRoute).all() == expected
    outcome = session.scalars(select(model.NewRoute)).all()
    print(outcome)
    assert outcome == expected
    session.close()


def test_orderline_mapper_can_save_lines(session):
    # delete all records first
    session.execute(delete(model.NewRoute))

    new_line = model.NewRoute("James", "RiverRd", 30, 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(text('SELECT rider, road, distance, mph, FROM "new_routes"')))
    assert rows == [("James", "RiverRd", 30, 12)]

    session.close()


def test_retrieving_batches(session):
    # delete all records first
    session.execute(delete(model.Ride))
    session.execute(
        text(
            "INSERT INTO rides (reference, road, miles, mph, eta)"
            ' VALUES ("ride1", "road1", 40, 23, null)'
        )
    )
    session.execute(
        text(
            "INSERT INTO rides (reference, road, miles, mph, eta)"
            ' VALUES ("ride2", "road2", 200, 23, "2011-04-11")'
        )
    )
    expected = [
        model.Ride("ride1", "road1", 40, 23, eta=None),
        model.Ride("ride2", "road2", 200, 23, eta=date(2011, 4, 11)),
    ]

    assert session.query(model.Ride).all() == expected

    session.close()


def test_saving_batches(session):
    # delete all records first
    session.execute(delete(model.Ride))
    ride = model.Ride("ride1", "road1", 40, 22, eta=None)
    session.add(ride)
    session.commit()
    rows = session.execute(
        text('SELECT reference, road, miles, mph, eta FROM "rides"')
    )
    assert list(rows) == [("ride1", "road1", 40, None)]

    session.close()


def test_saving_allocations(session):
    # delete all records first
    session.execute(delete(model.Ride))
    session.execute(delete(model.NewRoute))
    ride = model.Ride("ride1", "road1", 40, 22, eta=None)
    route = model.NewRoute("James", "road1", 25, 10)
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
    session.execute(delete(model.NewRoute))
    session.execute(
        text(
            'INSERT INTO new_routes (rider, road, distance, mph) VALUES ("James", "road1", 33, 12)'
        )
    )
    [[olid]] = session.execute(
        text("SELECT id FROM new_routes WHERE rider=:rider AND road=:road"),
        dict(rider="James", road="road1"),
    )
    session.execute(
        text(
            "INSERT INTO rides (reference, road, miles, mph, eta)"
            ' VALUES ("ride1", "road1", 40, 19, null)'
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

    assert ride._allocations == {model.NewRoute("James", "road1", 12)}

    session.close()
