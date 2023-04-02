import abc
import model

from sqlalchemy import select


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, ride: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, ride):
        self.session.add(ride)

    def get(self, reference):
        return self.session.scalars(
            select(model.Batch).filter_by(reference=reference)
        ).one()

    def list(self):
        return self.session.scalars(select(model.Batch)).all()
