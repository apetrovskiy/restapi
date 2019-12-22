# -*- coding: utf-8 -*-
"""
    Нагрузочное тестирование
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Для фикстуры client изменен scope на module. Это позволяет работать
    с одним экземпляром базы данных при проведении тестирования.

"""

import os
from typing import Iterable

import pytest
import tempfile

from flask import Flask
from flask.testing import FlaskClient

from api import create_app
from api.db import drop_db


@pytest.fixture(scope="module")
def app() -> Iterable[Flask]:
    app = create_app(config={
        'MONGO_URI': os.environ['MONGO_URI'],
        'MONGO_DBNAME': os.environ['MONGO_TESTDBNAME'],
        'LOG_FILE': tempfile.mktemp()
    })

    with app.app_context():
        drop_db()

    yield app


@pytest.fixture(scope="module")
def client(app: Flask) -> FlaskClient:
    return app.test_client()
