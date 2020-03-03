# -*- coding: utf-8 -*-
"""
    Фикстуры для тестов
    ~~~~~~~~~~~~~~~~~~~

    .. data
        Генерирует информацию о трех горожанах в базе данных. Гарантируется,
        что их id = [1, 2, 3], а первый находится с третьим в родственных
        отношениях. Возвращает import_id.

    Функции
    ~~~~~~~

    .. gen_ctzns(n: int) -> List[Dict[str, Union[int, str, List[int]]]]
        Генерирует информацию о горожанах. Гарантируется,
        что их id = [1, 2, ... n], а первый с последним находится
        в родственных отношениях.

"""

import os
from typing import List, Dict, Any

import pytest
import json

from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from api import create_app
from api.mongo_orm import drop_db

__all__ = ["gen_ctzns"]


@pytest.fixture()
def app() -> Flask:
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
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


def gen_ctzns(n: int) -> List[Dict[str, Any]]:
    """Генерирует информацию о горожанах. Гарантируется,
    что их id = [1, 2, ... n], а первый с последним находится
    в родственных отношениях.

    """

    ctzns: List[Dict[str, Any]] = [
        {
            "citizen_id": c_id,
            "town": "Мос kwa",
            "street": "123st",
            "building": "5",
            "apartment": 1,
            "name": "Иванов Иван Иванович",
            "birth_date": "17.08.2003",
            "gender": "male",
            "relatives": []
        } for c_id in range(1, n + 1)
    ]

    ctzns[-1]["relatives"] = [1]
    ctzns[0]["relatives"] = [n]

    return ctzns


@pytest.fixture()
def data3(client: FlaskClient) -> int:
    """
    Генерирует информацию о трех горожанах в базе данных. Гарантируется,
    что их id = [1, 2, 3], а первый находится с третьим в родственных
    отношениях. Возвращает import_id.

    """
    response = client.post(
        '/imports',
        data=json.dumps(
            {
                "citizens": gen_ctzns(3)
            }),
        content_type='application/json'
    )

    return json.loads(response.data)["data"]["import_id"]
