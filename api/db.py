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

    .. get_db()
        Экземпляр базы данных для операций.

    Команды
    ~~~~~~~

    .. drop-db
        Очищает основную и тестовую базы данных.

"""

import click
from pymongo import MongoClient
from flask import current_app, g
from flask.cli import with_appcontext

__all__ = ["get_db"]


def get_db():
    if 'client' not in g:
        g.client = MongoClient(current_app.config['MONGO_URI'])

    return g.client[current_app.config['MONGO_DB_NAME']]


def close_db(e=None):
    client = g.pop('client', None)

    if client is not None:
        client.close()


def drop_db():
    db = get_db()  # Добавляет client в g
    g.client.drop_database(current_app.config['MONGO_DB_NAME'])
    g.client.drop_database("test")
    close_db()


@click.command('drop-db')
@with_appcontext
def drop_db_command():
    drop_db()
    click.echo('Done.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(drop_db_command)
