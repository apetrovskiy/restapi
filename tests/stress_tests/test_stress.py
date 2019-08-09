# -*- coding: utf-8 -*-

import json

from tests.conftest import gen_ctzns


def test_c1(client):
    ctzns = gen_ctzns(10 ** 5)

    response = client.post(
        '/imports',
        data=json.dumps(
            {"citizens": ctzns}
        ),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert json.loads(response.data) == {
        "data": {
            "import_id": 1
        }
    }


def test_c2(client):
    response = client.patch(
        '/imports/1/citizens/1000',
        data=json.dumps(
            {
                "name": "Иванова Мария Леонидовна",
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "gender": "female",
                "relatives": list(range(100, 501))
            }
        ),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "citizen_id": 1000,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванова Мария Леонидовна",
            "birth_date": "12.12.2012",
            "gender": "female",
            "relatives": list(range(100, 501))
        }
    }


def test_c3(client):
    response = client.get('/imports/1/citizens')
    assert response.status_code == 200


def test_c4(client):
    response = client.get('/imports/1/citizens/birthdays')
    assert response.status_code == 200


def test_c5(client):
    response = client.get('/imports/1/towns/stat/percentile/age')
    assert response.status_code == 200
