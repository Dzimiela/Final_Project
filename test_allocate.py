from datetime import date, timedelta
import pytest
from model import allocate, OrderLine, Batch, RideCancelled

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-ride", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-ride", "RETRO-CLOCK", 100, eta=tomorrow)
    route = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(route, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-ride", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-ride", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-ride", "MINIMALIST-SPOON", 100, eta=later)
    route = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(route, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-ride-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-ride-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    route = OrderLine("oref", "HIGHBROW-POSTER", 10)
    allocation = allocate(route, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    ride = Batch("batch1", "SMALL-FORK", 10, eta=today)
    allocate(OrderLine("order1", "SMALL-FORK", 10), [ride])

    with pytest.raises(RideCancelled, match="SMALL-FORK"):
        allocate(OrderLine("order2", "SMALL-FORK", 1), [ride])
