# -*- coding: utf-8 -*-

import json


def test_nf_import(client):
    response = client.get('/imports/100/citizens')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": "Not found"
    }


def test_expected(client, data):
    response = client.get('/imports/1/towns/stat/percentile/age')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": [
            {
                "p50": 6.0,
                "p75": 6.0,
                "p99": 6.0,
                "town": "abc"
            }
        ]
    }
