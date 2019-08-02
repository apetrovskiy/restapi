# -*- coding: utf-8 -*-

import json


def test_no_import(client, post):
    response = client.get('/imports/2/citizens')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": "Not found"
    }


def test_expected(client, post):
    response = client.get('/imports/1/citizens')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": [
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
