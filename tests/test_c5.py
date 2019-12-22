# -*- coding: utf-8 -*-

import json


def test_nf_import(client, data):
    response = client.get('/imports/100/towns/stat/percentile/age')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": 404,
        "description": "import doesn't exist"
    }


def test_expected(client, data):
    response = client.get('/imports/1/towns/stat/percentile/age')
    assert response.status_code == 200
    assert "data" in json.loads(response.data)
    assert "p50" in json.loads(response.data)["data"][0]
    assert "p75" in json.loads(response.data)["data"][0]
    assert "p99" in json.loads(response.data)["data"][0]
