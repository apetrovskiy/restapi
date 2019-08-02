# -*- coding: utf-8 -*-

import json


def test_c1(client):
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

    response = client.post(
        '/imports',
        data=json.dumps(
            {
                "citizens": ctzns
            }),
        content_type='application/json')
    assert response.status_code == 201
    assert json.loads(response.data) == {
        "data": {
            "import_id": 1
        }
    }


def test_c2(client, post_10000):
    response = client.patch(
        '/imports/1/citizens/600',
        data=json.dumps(
            {
                "name": "Иванова Мария Леонидовна",
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "relatives": list(range(100, 501))
            }),
        content_type='application/json')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "citizen_id": 600,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванова Мария Леонидовна",
            "birth_date": "23.11.1986",
            "gender": "female",
            "relatives": list(range(100, 501))
        }
    }


def test_c3(client, post_10000):
    response = client.get('/imports/1/citizens')
    assert response.status_code == 200


def test_c4(client, post_10000):
    response = client.get('/imports/1/citizens/birthdays')
    assert response.status_code == 200


def test_c5(client, post_10000):
    response = client.get('/imports/1/towns/stat/percentile/age')
    assert response.status_code == 200
