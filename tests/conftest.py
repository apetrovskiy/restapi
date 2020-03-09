# -*- coding: utf-8 -*-

import os
from typing import Any, Mapping, Iterable

import pytest

from flask import Flask

from api import create_app
from api.citizen_schema import validate_import_citizens, Citizen
from api.mongo_orm import drop_db


from tests import Citizen_s


@pytest.fixture()
def app() -> Any:
    app = create_app(config={
        'MONGO_URI': os.environ['MONGO_URI'],
        'MONGO_DBNAME': os.environ['MONGO_TESTDBNAME'],
    })

    @app.route('/exc')
    def raise_exc() -> Any:
        """Для тестирования логирования"""
        return 1 / 0

    with app.app_context():
        drop_db()

    yield app


@pytest.fixture()
def client(app: Flask) -> Any:
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> Any:
    return app.test_cli_runner()


@pytest.fixture()
def data3() -> Iterable[Citizen_s]:
    return [
        {
            "citizen_id": 1,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Иван Иванович",
            "birth_date": "26.12.1986",
            "gender": "male",
            "relatives": [2]
        },
        {
            "citizen_id": 2,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Сергей Иванович",
            "birth_date": "17.04.1997",
            "gender": "male",
            "relatives": [1]
        },
        {
            "citizen_id": 3,
            "town": "Керчь",
            "street": "Иосифа Бродского",
            "building": "2",
            "apartment": 11,
            "name": "Романова Мария Леонидовна",
            "birth_date": "23.11.1986",
            "gender": "female",
            "relatives": []
        }
    ]


@pytest.fixture()
def data3d(data3: Citizen_s) -> Mapping[int, Citizen]:
    return validate_import_citizens(data3)
