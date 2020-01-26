# -*- coding: utf-8 -*-

import json


def test_nf_import(client):
    response = client.get('/imports/1/towns/stat/percentile/age')
    assert response.status_code == 404
    assert json.loads(response.data).get("error", None) == 404


def test_expected(client, data3):
    response = client.get(f'/imports/{data3}/towns/stat/percentile/age')
    assert response.status_code == 200
    assert "data" in json.loads(response.data)
    assert "p50" in json.loads(response.data)["data"][0]
    assert "p75" in json.loads(response.data)["data"][0]
    assert "p99" in json.loads(response.data)["data"][0]
