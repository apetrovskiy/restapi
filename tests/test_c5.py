# -*- coding: utf-8 -*-

import json


def test_no_import(client, post):
    response = client.get('/imports/2/citizens')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": "Not found"
    }


def test_expected(client, post):
    response = client.get('/imports/1/towns/stat/percentile/age')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": [
            {
                'p50': 27.0,
                'p75': 29.5,
                'p99': 31.9,
                'town': 'Москва'
            },
            {
                'p50': 32.0,
                'p75': 32.0,
                'p99': 32.0,
                'town': 'Керчь'
            }
        ]
    }
