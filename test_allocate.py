from datetime import date, timedelta
import pytest
from model import allocate, OrderLine, Ride, RideCancelled

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Ride("in-stock-ride", "FlandersRd", 100, eta=None)
    shipment_batch = Ride("shipment-ride", "FlandersRd", 100, eta=tomorrow)
    route = OrderLine("oref", "FlandersRd", 10)

    allocate(route, [in_stock_batch, shipment_batch])

    assert in_stock_batch.total_miles == 90
    assert shipment_batch.total_miles == 100


def test_prefers_earlier_batches():
    short = Ride("speedy-ride", "RoubaixStreet", 100, eta=today)
    medium = Ride("normal-ride", "RoubaixStreet", 100, eta=tomorrow)
    latest = Ride("slow-ride", "RoubaixStreet", 100, eta=later)
    route = OrderLine("James", "RoubaixStreet", 10)

    allocate(route, [medium, short, latest])

    assert short.total_miles == 90
    assert medium.total_miles == 100
    assert latest.total_miles == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Ride("in-stock-ride-ref", "BigStreetCreek", 100, eta=None)
    shipment_batch = Ride("shipment-ride-ref", "BigStreetCreek", 100, eta=tomorrow)
    route = OrderLine("oref", "BigStreetCreek", 10)
    allocation = allocate(route, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    ride = Ride("batch1", "BackAlleyRoad", 10, eta=today)
    allocate(OrderLine("James", "BackAlleyRoad", 10), [ride])

    with pytest.raises(RideCancelled, match="BackAlleyRoad"):
        allocate(OrderLine("Steve", "BackAlleyRoad", 1), [ride])
