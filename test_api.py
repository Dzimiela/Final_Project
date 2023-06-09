import uuid
import pytest
import requests
import config

from datetime import datetime


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_road(name=""):
    return f"road-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"ride-{name}-{random_suffix()}"


def random_rider(name=""):
    return f"order-{name}-{random_suffix()}"


def test_api_works(test_client):
    url = config.get_api_url()
    r = test_client.get(f"{url}/")
    assert r.status_code == 200
    assert b"HELLO FROM THE API" in r.data

'''
def test_happy_path_returns_201_and_allocated_batch(add_ride, test_client):
    road, otherroad = random_road("ball"), random_road("other")
    print(road)
    earlyride = random_batchref(1)
    laterride = random_batchref(2)
    otherride = random_batchref(3)
    add_ride(
        [
            (laterride, road, 40,25, datetime.strptime("2011-01-02", "%Y-%m-%d")),
            (earlyride, road, 40, 15, datetime.strptime("2011-01-01", "%Y-%m-%d")),
            (otherride, otherroad, 40, 17, None),
        ]
    )
    data = {"rider": random_rider(), "road": road, "distance": 3}
    url = config.get_api_url()
    r = test_client.post(f"{url}/allocate", json=data)
    # r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 201
    assert r.json["batchref"] == earlyride


def test_unhappy_path_returns_400_and_error_message(test_client):
    unknown_road, rider = random_road(), random_rider()
    data = {"rider": rider, "road": unknown_road, "distance": 20}
    url = config.get_api_url()
    r = test_client.post(f"{url}/allocate", json=data)
    # r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json["message"] == f"Invalid road {unknown_road}"
'''