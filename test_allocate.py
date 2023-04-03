from datetime import date, timedelta
import pytest
from model import allocate, NewRoute, Ride, RideCancelled

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_speed_high_or_Low():
    mapped_road = Ride("afternoon-ride", "FlandersRd", 35, 13, eta=today)
    not_mapped_road = Ride("dirty-ride", "FlandersRd", 34, 25, eta=tomorrow)
    route = NewRoute("oref", "FlandersRd", 10)

    allocate(route, [mapped_road, not_mapped_road])

    assert mapped_road.speed_mph <= 15, "Slower Ride, below 15MPH"
    assert not_mapped_road.speed_mph >= 15, "Faster Ride, Above 15MPH"


def test_determine_ride_length():
    short = Ride("speedy-ride", "RoubaixStreet", 14, 20, eta=today)
    medium = Ride("normal-ride", "RoubaixStreet", 37, 21, eta=tomorrow)
    long = Ride("slow-ride", "RoubaixStreet", 49, 19, eta=later)
    route = NewRoute("James", "RoubaixStreet", 10)

    allocate(route, [medium, short, long])

    assert short.total_miles < 15
    assert medium.total_miles >=15 or medium.total_miles <=39
    assert long.total_miles >= 40


def test_returns_allocated_batch_ref():
    mapped_road = Ride("afternoon-ride-ref", "BigStreetCreek", 40, 16, eta=None)
    not_mapped_road = Ride("dirty-ride-ref", "BigStreetCreek", 40, 17, eta=tomorrow)
    route = NewRoute("oref", "BigStreetCreek", 10)
    allocation = allocate(route, [mapped_road, not_mapped_road])
    assert allocation == mapped_road.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    ride = Ride("ride1", "BackAlleyRoad", 10, 19, eta=today)
    allocate(NewRoute("James", "BackAlleyRoad", 10), [ride])

    with pytest.raises(RideCancelled, match="BackAlleyRoad"):
        allocate(NewRoute("Steve", "BackAlleyRoad", 1), [ride])
