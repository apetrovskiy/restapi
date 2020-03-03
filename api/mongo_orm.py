# -*- coding: utf-8 -*-
import datetime

from bson import ObjectId
from typing import Optional, Mapping, cast, Any

import click
from pymongo import MongoClient, UpdateOne
from pymongo.database import Database
from flask import current_app, g, Flask
from flask.cli import with_appcontext
from pymongo.errors import ConnectionFailure

from api.citizen_schema import NotFound, Citizen, CitizenSchema

__all__ = [
    "create", "update", "read", "delete", "get_db", "drop_db",
    "ConnectionFailure"
]


def get_db() -> Database:
    if 'client' not in g:
        g.client = MongoClient(current_app.config['MONGO_URI'])

    return g.client[current_app.config['MONGO_DBNAME']]


def close_db(e: Optional[Exception] = None) -> None:
    if e is not None:
        current_app.logger.error(e)

    client = g.pop('client', None)

    if client is not None:
        client.close()


def drop_db() -> None:
    get_db()  # Добавляет client в g
    g.client.drop_database(current_app.config['MONGO_DBNAME'])
    close_db()


@click.command('drop-db')
@with_appcontext
def drop_db_command() -> None:
    drop_db()
    click.echo(f"database {current_app.config['MONGO_DBNAME']} is dropped.")


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(drop_db_command)


def create(citizens_data: Mapping[int, Citizen]) -> str:
    citizens_data = CitizenSchema().dump(citizens_data.values(), many=True)
    current_time = datetime.datetime.utcnow()

    try:
        result = get_db().imports.insert_one(
            {
                "citizens": citizens_data,
                "created": current_time,
                "last_updated": current_time
            }
        )
    finally:
        g.client.close()

    return str(result.inserted_id)


def read(import_id: str) -> Mapping[int, Citizen]:
    """Возвращает набор с данными о жителях."""
    try:
        citizens_data = get_db().imports.find_one(
            {"_id": ObjectId(import_id)},
            {"_id": 0}
        )
    finally:
        g.client.close()

    if not citizens_data:
        raise NotFound('import doesn\'t exist')

    citizens_data = CitizenSchema().load(citizens_data["citizens"], many=True)

    return {citizen.citizen_id: citizen for citizen in citizens_data}


def update(import_id: str, different_citizens: Mapping[int, Citizen]) -> None:
    different_citizens = CitizenSchema().dump(
        different_citizens.values(), many=True
    )

    operations = [
        UpdateOne({
            "_id": ObjectId(import_id),
            "citizens.citizen_id": cast(
                Mapping[str, Any], citizen)["citizen_id"]
        }, {
            "$set": {
                "citizens.$": citizen
            }
        }) for citizen in different_citizens
    ] + [
        UpdateOne(
            {
                "_id": ObjectId(import_id)
            }, {
                "$set": {
                    "last_updated": datetime.datetime.utcnow()
                }
            })
    ]

    try:
        get_db().imports.bulk_write(operations, ordered=False)
    finally:
        g.client.close()


def delete(import_id: str) -> None:
    try:
        n = get_db().imports.delete_one(
            {"_id": ObjectId(import_id)}).raw_result["n"]
    finally:
        g.client.close()

    if n == 0:
        raise NotFound('import doesn\'t exist')
