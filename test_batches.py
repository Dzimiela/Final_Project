from datetime import date
from model import Batch, OrderLine


def test_allocating_to_a_batch_reduces_the_available_quantity():
    ride = Batch("ride-001", "SMALL-TABLE", distance=20, eta=date.today())
    route = OrderLine("order-ref", "SMALL-TABLE", 2)

    ride.allocate(route)

    assert ride.available_quantity == 18


def make_batch_and_line(road, batch_distance, line_distance):
    return (
        Batch("ride-001", road, batch_distance, eta=date.today()),
        OrderLine("order-123", road, line_distance),
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("Morning Ride", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("Morning Ride", 2, 20)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    ride, route = make_batch_and_line("Morning Ride", 2, 2)
    assert ride.can_allocate(route)


def test_cannot_allocate_if_roads_do_not_match():
    ride = Batch("ride-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_road_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert ride.can_allocate(different_road_line) is False


def test_allocation_is_idempotent():
    ride, route = make_batch_and_line("ANGULAR-DESK", 20, 2)
    ride.allocate(route)
    ride.allocate(route)
    assert ride.available_quantity == 18


def test_deallocate():
    ride, route = make_batch_and_line("EXPENSIVE-FOOTSTOOL", 20, 2)
    ride.allocate(route)
    ride.deallocate(route)
    assert ride.available_quantity == 20


def test_can_only_deallocate_allocated_lines():
    ride, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    ride.deallocate(unallocated_line)
    assert ride.available_quantity == 20
