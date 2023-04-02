import pytest
import model
import repository
import services


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, ride):
        self._batches.add(ride)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    route = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    ride = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([ride])

    result = services.allocate(route, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_road():
    route = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    ride = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([ride])

    with pytest.raises(services.InvalidSku, match="Invalid road NONEXISTENTSKU"):
        services.allocate(route, repo, FakeSession())


def test_commits():
    route = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    ride = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([ride])
    session = FakeSession()

    services.allocate(route, repo, session)
    assert session.committed is True
