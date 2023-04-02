from datetime import date
from model import Ride, OrderLine


def test_allocating_to_a_batch_reduces_the_available_quantity():
    ride = Ride("ride-001", "ShortRideAroundHouse", distance=20, eta=date.today())
    route = OrderLine("order-ref", "ShortRideAroundHouse", 2)

    ride.allocate(route)

    assert ride.total_miles == 18


def make_batch_and_line(road, batch_distance, line_distance):
    return (
        Ride("ride-001", road, batch_distance, eta=date.today()),
        OrderLine("order-123", road, line_distance),
    )


def test_can_allocate_if_available_greater_than_required():
    large_ride, small_route = make_batch_and_line("Morning Ride", 20, 2)
    assert large_ride.can_allocate(small_route)


def test_cannot_allocate_if_available_smaller_than_required():
    short_ride, large_route = make_batch_and_line("Morning Ride", 2, 20)
    assert short_ride.can_allocate(large_route) is False


def test_can_allocate_if_available_equal_to_required():
    ride, route = make_batch_and_line("Morning Ride", 2, 2)
    assert ride.can_allocate(route)


def test_cannot_allocate_if_roads_do_not_match():
    ride = Ride("ride-001", "COLD-RIDE", 100, eta=None)
    different_road_line = OrderLine("order-123", "SUNDAY_FUNDAY_RIDE", 10)
    assert ride.can_allocate(different_road_line) is False


def test_allocation_is_idempotent():
    ride, route = make_batch_and_line("Friday-Night-Ride", 20, 2)
    ride.allocate(route)
    ride.allocate(route)
    assert ride.total_miles == 18


def test_deallocate():
    ride, route = make_batch_and_line("Pre-Race-Ride", 20, 2)
    ride.allocate(route)
    ride.deallocate(route)
    assert ride.total_miles == 20


def test_can_only_deallocate_allocated_lines():
    ride, unallocated_line = make_batch_and_line("Night-Ride", 20, 2)
    ride.deallocate(unallocated_line)
    assert ride.total_miles == 20
