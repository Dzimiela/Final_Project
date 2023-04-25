from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

import config
import model
import orm
import repository
import services


def index_endpoint():
    return "<p>HELLO FROM THE API</p>"


def allocate_endpoint():
    clear_mappers()
    orm.start_mappers()
    get_session = sessionmaker(bind=create_engine(config.get_sqlite_filedb_uri()))
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    route = model.NewRoute(
        request.json["rider"],
        request.json["road"],
        request.json["distance"],
        request.json["mph"],
    )

    try:
        batchref = services.allocate(route, repo, session)
    except (model.RideCancelled, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201


def create_app():
    app = Flask(__name__)
    app.config.update({"Route Test": True})

    app.add_url_rule("/", "index", view_func=index_endpoint)
    app.add_url_rule(
        "/allocate", "allocate", view_func=allocate_endpoint, methods=["POST"]
    )

    return app
#