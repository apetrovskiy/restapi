from pymongo import MongoClient
import click
from flask import current_app, g
from flask.cli import with_appcontext


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


@click.command('drop-db')
@with_appcontext
def drop_db_command():
    drop_db()
    click.echo('База данных очищена.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(drop_db_command)
