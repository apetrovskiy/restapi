# -*- coding: utf-8 -*-

import pytest
import json

from api.db import get_db


def test_post_import(client):
    response = client.post(
        '/imports',
        data=json.dumps({"citizens": [{"citizen_id": 1, "name": "ivan"}]}),
        content_type='application/json')
    assert response.status_code == 201
    assert json.loads(response.data) == {"data": {"import_id": 1}}


def test_get_citizens(client):
    test_post_import(client)
    response = client.get('/imports/1/citizens')
    assert response.status_code == 200
    assert json.loads(response.data) == {"data": [{"citizen_id": 1, "name": "ivan"}]}


def test_patch_citizens(client):
    test_post_import(client)
    response = client.patch(
        '/imports/1/citizens/1',
        data=json.dumps({"name": "not_ivan"}),
        content_type='application/json')
    assert response.status_code == 200
    assert json.loads(response.data) == {"data": {"citizen_id": 1, "name": "not_ivan"}}
