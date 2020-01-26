# -*- coding: utf-8 -*-

import json


def test_nf_import(client):
    response = client.get('/imports/1/citizens')
    assert response.status_code == 404
    assert json.loads(response.data).get("error", None) == 404


def test_expected(client, data3):
    response = client.get(f'/imports/{data3}/citizens')
    assert response.status_code == 200
    data = json.loads(response.data).get("data", [])

    ctzns = {int(ctzn["citizen_id"]): ctzn for ctzn in data}
    assert set(ctzns.keys()) == {1, 2, 3}
    assert ctzns[1]["relatives"] == [3]
    assert ctzns[3]["relatives"] == [1]
