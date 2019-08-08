# -*- coding: utf-8 -*-

import pytest
import json

from api import create_app
from api.db import drop_db


@pytest.fixture
def app():
    app = create_app()
    app.config.from_mapping({
        'TESTING': True,
        'MONGO_DB_NAME': 'test'
    })

    with app.app_context():
        drop_db()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def post(client):
    client.post(
        '/imports',
        data=json.dumps(
            {
                "citizens": [
                    {
                        "citizen_id": 1,
                        "town": "Москва",
                        "street": "Льва Толстого",
                        "building": "16к7стр5",
                        "apartment": 7,
                        "name": "Иванов Иван Иванович",
                        "birth_date": " 26.12.1986",
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
            }),
        content_type='application/json'
    )


@pytest.fixture
def post_10000(client):
    ctzns = []

    for c_id in range(1, 10001):
        ctzn = {
            "citizen_id": c_id,
            "town": "Керчь",
            "street": "Иосифа Бродского",
            "building": "2",
            "apartment": 11,
            "name": "Романова Мария Леонидовна",
            "birth_date": "23.11.1986",
            "gender": "female",
            "relatives": [10001-c_id]
        }
        ctzns.append(ctzn)

    client.post(
        '/imports',
        data=json.dumps(
            {
                "citizens": ctzns
            }),
        content_type='application/json')
