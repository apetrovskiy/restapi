# -*- coding: utf-8 -*-

import json
from bson import ObjectId


def test_empty_json(client, data3):
    response = client.patch(
        f'/imports/{data3}/citizens/3',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data).get("error", None) == 400


def test_nf_import(client):
    response = client.patch(
        f'/imports/{str(ObjectId())}/citizens/3',
        data=json.dumps(
            {"name": "Иванова Мария Леонидовна"}),
        content_type='application/json'
    )
    assert response.status_code == 404
    assert json.loads(response.data).get("error", None) == 404


def test_nf_citizen(client, data3):
    response = client.patch(
        f'/imports/{data3}/citizens/10',
        data=json.dumps(
            {"name": "Иванова Мария Леонидовна"}),
        content_type='application/json'
    )
    assert response.status_code == 404
    assert json.loads(response.data).get("error", None) == 404


def test_without_rels(client, data3):
    response = client.patch(
        f'/imports/{data3}/citizens/3',
        data=json.dumps(
            {"name": "Иванова Мария Леонидовна"}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get("data", {}).get("citizen_id") == 3


def test_add_rels(client, data3):
    response = client.patch(
        f'/imports/{data3}/citizens/3',
        data=json.dumps(
            {"relatives": [1, 2]}),
        content_type='application/json'
    )
    assert response.status_code == 200

    ctzns = json.loads(client.get(
        f'/imports/{data3}/citizens').data).get("data", [])
    ctzns = {int(ctzn["citizen_id"]): ctzn for ctzn in ctzns}

    assert 3 in ctzns[2]["relatives"]
    assert 3 in ctzns[1]["relatives"]


def test_rem_rels(client, data3):
    response = client.patch(
        f'/imports/{data3}/citizens/1',
        data=json.dumps(
            {"relatives": []}),
        content_type='application/json'
    )
    assert response.status_code == 200

    ctzns = json.loads(client.get(
        f'/imports/{data3}/citizens').data).get("data", [])
    ctzns = {int(ctzn["citizen_id"]): ctzn for ctzn in ctzns}

    assert ctzns[3]["relatives"] == []


def test_invalid_rel(client, data3):
    response = client.patch(
        f'/imports/{data3}/citizens/3',
        data=json.dumps({
            "relatives": [100]}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data).get("error", None) == 400
