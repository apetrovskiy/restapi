# -*- coding: utf-8 -*-

import json
from bson import ObjectId


def test_nf_import(client):
    response = client.get(f'/imports/{str(ObjectId())}/citizens/birthdays')
    assert response.status_code == 404
    assert json.loads(response.data).get("error", None) == 404


def test_expected(client, data3):
    response = client.get(f'/imports/{data3}/citizens/birthdays')
    assert response.status_code == 200
    data = json.loads(response.data).get("data", {})
    assert set(int(s) for s in data.keys()) == set(range(1, 13))
    assert type(data['1']) == list
