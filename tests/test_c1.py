# -*- coding: utf-8 -*-

import json

from api.db import get_db


def test_not_json(client):
    response = client.post(
        '/imports',
        data="text"
    )
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "data must be object"
    }


def test_emty_json(client):
    response = client.post(
        '/imports',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "data must contain ['citizens'] properties"
    }


def test_invalid_rels(client):
    response = client.post(
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
                        "relatives": []
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
                    }
                ]
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "citizens relatives are not bidirectional"
    }


def test_invalid_month(client):
    response = client.post(
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
                        "birth_date": " 26.13.1986",
                        "gender": "male",
                        "relatives": []
                    }
                ]
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "month must be in 1..12"
    }


def test_invalid_day(client):
    response = client.post(
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
                        "birth_date": "31.02.1986",
                        "gender": "male",
                        "relatives": []
                    }
                ]
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "day is out of range for month"
    }


def test_string_max_length(client):
    response = client.post(
        '/imports',
        data=json.dumps(
            {
                "citizens": [
                    {
                        "citizen_id": 1,
                        "town": "М" * 257,
                        "street": "Льва Толстого",
                        "building": "16к7стр5",
                        "apartment": 7,
                        "name": "Иванов Иван Иванович",
                        "birth_date": "31.02.1986",
                        "gender": "male",
                        "relatives": []
                    }
                ]
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "data must be shorter than or equal to 256 characters"
    }


def test_not_unique_ids(client):
    response = client.post(
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
                        "citizen_id": 1,
                        "town": "Москва",
                        "street": "Льва Толстого",
                        "building": "16к7стр5",
                        "apartment": 7,
                        "name": "Иванов Сергей Иванович",
                        "birth_date": "17.04.1997",
                        "gender": "male",
                        "relatives": [1]
                    }
                ]
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "citizen_ids are not unique"
    }


def test_expected(client, app):
    response = client.post(
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
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert json.loads(response.data) == {
        "data": {
            "import_id": 1
        }
    }
    with app.app_context():
        db = get_db()
        ctzns = db.imports.find_one({"_id": 1})
        assert ctzns == {
            "_id": 1,
            "1": {
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
            "2": {
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
            "3": {
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
        }
