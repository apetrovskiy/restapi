# -*- coding: utf-8 -*-
"""
    Нагрузочное тестирование
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Для фикстуры client изменен scope на module. Это позволяет работать с
    одним экземпляром базы данных при проведении тестирования.
"""

import pytest
import tempfile

from api import create_app
from api.db import drop_db


@pytest.fixture(scope="module")
def app():
    app = create_app(config={
        'TESTING': True,
        'MONGO_URI': 'mongodb://localhost:27017/',
        'MONGO_DB_NAME': 'test',
        'LOGS_DIR': tempfile.mkdtemp()
    })

    with app.app_context():
        drop_db()

    yield app


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()
