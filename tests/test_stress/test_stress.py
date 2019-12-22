# -*- coding: utf-8 -*-
"""
    Нагрузочное тестирование
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Тесты проверяют только коды ответов, но не тела.

"""

import json


def test_c1(client, more_data):
    response = client.post(
        '/imports',
        data=json.dumps(
            {"citizens": more_data}
        ),
        content_type='application/json'
    )
    assert response.status_code == 201


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


def test_c3(client):
    response = client.get('/imports/1/citizens')
    assert response.status_code == 200


def test_c4(client):
    response = client.get('/imports/1/citizens/birthdays')
    assert response.status_code == 200


def test_c5(client):
    response = client.get('/imports/1/towns/stat/percentile/age')
    assert response.status_code == 200
