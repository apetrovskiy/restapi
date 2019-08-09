# -*- coding: utf-8 -*-

import json

from api.db import get_db


def test_not_json(client, data):
    response = client.patch(
        '/imports/1/citizens/3',
        data="text"
    )
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "data must be object"
    }


def test_empty_json(client, data):
    response = client.patch(
        '/imports/1/citizens/3',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request",
        "description": "data must contain at least 1 properties"
    }


def test_nf_import(client):
    response = client.patch(
        '/imports/100/citizens/3',
        data=json.dumps(
            {
                "name": "Иванова Мария Леонидовна",
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "relatives": [1]
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": "Not found"
    }


def test_nf_citizen(client):
    response = client.patch(
        '/imports/1/citizens/100',
        data=json.dumps(
            {
                "name": "Иванова Мария Леонидовна",
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "relatives": [1]
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": "Not found"
    }


def test_without_rels(client, app, data):
    response = client.patch(
        '/imports/1/citizens/3',
        data=json.dumps(
            {
                "gender": "male"
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "citizen_id": 3,
            "town": "abc",
            "street": "abc",
            "building": "abc",
            "apartment": 1,
            "name": "abc",
            "gender": "male",
            "birth_date": "12.12.2012",
            "relatives": [1]
        }
    }
    with app.app_context():
        db = get_db()
        ctzn = db.imports.find_one({"_id": 1})["3"]
        assert ctzn == {
            "citizen_id": 3,
            "town": "abc",
            "street": "abc",
            "building": "abc",
            "apartment": 1,
            "name": "abc",
            "gender": "male",
            "birth_date": "12.12.2012",
            "relatives": [1]
        }


def test_add_rels(client, app, data):
    response = client.patch(
        '/imports/1/citizens/3',
        data=json.dumps(
            {
                "relatives": [1, 2],
                "gender": "female"
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "citizen_id": 3,
            "town": "abc",
            "street": "abc",
            "building": "abc",
            "apartment": 1,
            "name": "abc",
            "gender": "female",
            "birth_date": "12.12.2012",
            "relatives": [1, 2]
        }
    }
    with app.app_context():
        db = get_db()
        assert db.imports.find_one({"_id": 1})["2"]["relatives"] == [3]

        ctzn = db.imports.find_one({"_id": 1})["3"]
        assert ctzn == {
            "citizen_id": 3,
            "town": "abc",
            "street": "abc",
            "building": "abc",
            "apartment": 1,
            "name": "abc",
            "gender": "female",
            "birth_date": "12.12.2012",
            "relatives": [1, 2]
        }


def test_rem_rels(client, app, data):
    response = client.patch(
        '/imports/1/citizens/1',
        data=json.dumps(
            {
                "relatives": [],
                "gender": "male"
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "citizen_id": 1,
            "town": "abc",
            "street": "abc",
            "building": "abc",
            "apartment": 1,
            "name": "abc",
            "birth_date": "12.12.2012",
            "gender": "male",
            "relatives": []
        }
    }

    with app.app_context():
        db = get_db()
        assert db.imports.find_one({"_id": 1})["3"]["relatives"] == []
