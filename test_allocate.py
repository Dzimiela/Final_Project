from datetime import date, timedelta
import pytest
from model import allocate, NewRoute, Ride, RideCancelled

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    mapped_road = Ride("in-stock-ride", "FlandersRd", 40, eta=None)
    not_mapped_road = Ride("shipment-ride", "FlandersRd", 40, eta=tomorrow)
    route = NewRoute("oref", "FlandersRd", 10)

    allocate(route, [mapped_road, not_mapped_road])

    assert mapped_road.total_miles == 15
    assert not_mapped_road.total_miles == 40


def test_prefers_earlier_batches():
    short = Ride("speedy-ride", "RoubaixStreet", 40, eta=today)
    medium = Ride("normal-ride", "RoubaixStreet", 40, eta=tomorrow)
    long = Ride("slow-ride", "RoubaixStreet", 40, eta=later)
    route = NewRoute("James", "RoubaixStreet", 10)

    allocate(route, [medium, short, long])

    assert short.total_miles == 15
    assert medium.total_miles == 40
    assert long.total_miles == 40


def test_returns_allocated_batch_ref():
    mapped_road = Ride("in-stock-ride-ref", "BigStreetCreek", 40, eta=None)
    not_mapped_road = Ride("shipment-ride-ref", "BigStreetCreek", 40, eta=tomorrow)
    route = NewRoute("oref", "BigStreetCreek", 10)
    allocation = allocate(route, [mapped_road, not_mapped_road])
    assert allocation == mapped_road.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    ride = Ride("ride1", "BackAlleyRoad", 10, eta=today)
    allocate(NewRoute("James", "BackAlleyRoad", 10), [ride])

    with pytest.raises(RideCancelled, match="BackAlleyRoad"):
        allocate(NewRoute("Steve", "BackAlleyRoad", 1), [ride])
