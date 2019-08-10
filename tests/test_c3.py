# -*- coding: utf-8 -*-

import json


def test_nf_import(client, data):
    response = client.get('/imports/100/citizens')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": "Not Found",
        "description": "import doesn't exist"
    }


def test_expected(client, data):
    response = client.get('/imports/1/citizens')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": [
            {
                "citizen_id": 1,
                "town": "abc",
                "street": "abc",
                "building": "abc",
                "apartment": 1,
                "name": "abc",
                "birth_date": "12.12.2012",
                "gender": "male",
                "relatives": [3]
            },
            {
                "citizen_id": 2,
                "town": "abc",
                "street": "abc",
                "building": "abc",
                "apartment": 1,
                "name": "abc",
                "birth_date": "12.12.2012",
                "gender": "male",
                "relatives": []
            },
            {
                "citizen_id": 3,
                "town": "abc",
                "street": "abc",
                "building": "abc",
                "apartment": 1,
                "name": "abc",
                "birth_date": "12.12.2012",
                "gender": "male",
                "relatives": [1]
            }
        ]
    }
