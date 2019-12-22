# -*- coding: utf-8 -*-
"""
    Структура db.imports
    ~~~~~~~~~~~~~~~~~~~~

    [
        {
            "_id": 1,  // import_id
            "1": {"citizen_id": 1, "town": ...},
            "2": {"citizen_id": 2, "town": ...},
            ...
        },
        ...
    ]

    Хранение жителей в словаре увеличивает скорость доступа к отдельному
    жителю.

    Функции
    ~~~~~~~

    .. get_db() -> Database
        Экземпляр базы данных для операций.

    Команды
    ~~~~~~~

    .. drop-db
        Очищает основную базу данных.

"""

import click
from pymongo import MongoClient
from pymongo.database import Database
from flask import current_app, g, Flask
from flask.cli import with_appcontext

__all__ = ["get_db", "drop_db"]


def get_db() -> Database:
    if 'client' not in g:
        g.client = MongoClient(current_app.config['MONGO_URI'])

    return g.client[current_app.config['MONGO_DBNAME']]


def close_db(e=None) -> None:
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
