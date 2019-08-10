# -*- coding: utf-8 -*-

import os

from api import create_app
from api.db import drop_db

import pytest


@pytest.fixture()
def app(tmpdir):
    tmpdir.mkdir('logs')
    os.environ['LOGS_DIR'] = 'teststemp/logs/'
    app = create_app()
    app.config.from_mapping({
        'TESTING': True,
        'MONGO_DB_NAME': 'test'
    })

    @app.route('/exc')
    def raise_exc():
        raise ZeroDivisionError("some text")

    with app.app_context():
        drop_db()

    yield app

    os.environ.pop('LOGS_DIR')


@pytest.fixture()
def client(app):
    return app.test_client()
