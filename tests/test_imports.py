# -*- coding: utf-8 -*-

import json

from api.db import get_db


def test_post_imp_val_rels(client):
    # Недвусторонние родственные связи
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
            }),
        content_type='application/json')
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request"
    }


def test_post_imp_val_date(client):
    # Неправильный месяц в дате
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
            }),
        content_type='application/json')
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "error": "Bad Request"
    }


def test_post_imp(client):
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
            }),
        content_type='application/json')
    assert response.status_code == 201
    assert json.loads(response.data) == {
        "data": {
            "import_id": 1
        }
    }


def test_patch_ctzns(client):
    test_post_imp(client)
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


def test_get_ctzns(client):
    test_patch_ctzns(client)
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
                "relatives": [2, 3]
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
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванова Мария Леонидовна",
                "birth_date": "23.11.1986",
                "gender": "female",
                "relatives": [1]
            }
        ]
    }


def test_get_birthdays(client):
    test_patch_ctzns(client)
    response = client.get('/imports/1/citizens/birthdays')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "1": [],
            "2": [],
            "3": [],
            "4": [{
                "citizen_id": 1,
                "presents": 1,
                 }],
            "5": [],
            "6": [],
            "7": [],
            "8": [],
            "9": [],
            "10": [],
            "11": [{
                "citizen_id": 1,
                "presents": 1
                  }],
            "12": [
                {
                    "citizen_id": 2,
                    "presents": 1
                },
                {
                    "citizen_id": 3,
                    "presents": 1
                }
                ]
            }
        }


def test_get_age_stat(client):
    test_get_birthdays(client)
    response = client.get('/imports/1/towns/stat/percentile/age')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": [
            {
                "town": "Москва",
                "p50": 32,
                "p75": 32,
                "p99": 32
            }
        ]
    }
