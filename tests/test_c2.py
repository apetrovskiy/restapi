# -*- coding: utf-8 -*-

import json

from api.db import get_db


def test_plain_text(client, post):
    response = client.patch(
        '/imports/1/citizens/3',
        data="plain text")
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "data must be object"
    }


def test_empty_json(client, post):
    response = client.patch(
        '/imports/1/citizens/3',
        data=json.dumps({}),
        content_type='application/json')
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "data must contain at least 1 properties"
    }


def test_no_import(client, post):
    response = client.patch(
        '/imports/2/citizens/3',
        data=json.dumps(
            {
                "name": "Иванова Мария Леонидовна",
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "relatives": [1]
            }),
        content_type='application/json')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": "Not found"
    }


def test_no_citizen(client, post):
    response = client.patch(
        '/imports/1/citizens/4',
        data=json.dumps(
            {
                "name": "Иванова Мария Леонидовна",
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "relatives": [1]
            }),
        content_type='application/json')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": "Not found"
    }


def test_without_rels(client, post, app):
    response = client.patch(
        '/imports/1/citizens/3',
        data=json.dumps(
            {
                "name": "Иванова Мария Леонидовна",
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "relatives": []
            }),
        content_type='application/json')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "citizen_id": 3,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванова Мария Леонидовна",
            "birth_date": "23.11.1986",
            "gender": "female",
            "relatives": []
        }
    }
    with app.app_context():
        db = get_db()
        ctzn = db.imports.find_one({"_id": 1})["3"]
        assert ctzn == {
            "citizen_id": 3,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванова Мария Леонидовна",
            "birth_date": "23.11.1986",
            "gender": "female",
            "relatives": []
        }


def test_expected(client, app, post):
    response = client.patch(
        '/imports/1/citizens/3',
        data=json.dumps(
            {
                "name": "Иванова Мария Леонидовна",
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "relatives": [1]
            }),
        content_type='application/json')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "citizen_id": 3,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванова Мария Леонидовна",
            "birth_date": "23.11.1986",
            "gender": "female",
            "relatives": [1]
        }
    }
    with app.app_context():
        db = get_db()
        assert db.imports.find_one({"_id": 1})["1"]["relatives"] == [2, 3]

        ctzn = db.imports.find_one({"_id": 1})["3"]
        assert ctzn == {
            "citizen_id": 3,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванова Мария Леонидовна",
            "birth_date": "23.11.1986",
            "gender": "female",
            "relatives": [1]
        }


def test_remove_rels(client, app, post):
    response = client.patch(
        '/imports/1/citizens/1',
        data=json.dumps(
            {
                "relatives": []
            }),
        content_type='application/json')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "citizen_id": 1,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Иван Иванович",
            "birth_date": " 26.12.1986",
            "gender": "male",
            "relatives": []
        }
    }

    with app.app_context():
        db = get_db()
        assert db.imports.find_one({"_id": 1})["2"]["relatives"] == []
