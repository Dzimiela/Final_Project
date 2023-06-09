from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import registry, relationship

import model

# https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#imperative-mapping
# using SQLAlchemy 2.0-style imperative mapping
mapper_registry = registry()

new_routes = Table(
    "new_routes",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("road", String(255)),
    Column("distance", Integer, nullable=False),
    Column("mph", Integer, nullable=False),
    Column("rider", String(255)),
)

rides = Table(
    "rides",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("road", String(255)),
    Column("miles", Integer, nullable=False),
    Column("mph", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("new_routes.id")),
    Column("batch_id", ForeignKey("rides.id")),
)

def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(model.NewRoute, new_routes)
    mapper_registry.map_imperatively(
        model.Ride,
        rides,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
#