# -*- coding: utf-8 -*-

import pytest
import random
import json

from api import create_app
from api.db import drop_db


@pytest.fixture()
def app():
    app = create_app()
    app.config.from_mapping({
        'TESTING': True,
        'MONGO_DB_NAME': 'test'
    })

    with app.app_context():
        drop_db()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def gen_ctzns(n):
    ctzns = []

    if n > 10:
        n_rels = n // 5
    else:
        n_rels = n

    for c_id in range(1, n + 1):
        ctzn = {
            "citizen_id": c_id,
            "town": "abc",
            "street": "abc",
            "building": "abc",
            "apartment": 1,
            "name": "abc",
            "birth_date": "12.12.2012",
            "gender": "male",
            "relatives": []
        }
        ctzns.append(ctzn)

    for c_id in range(1, n_rels + 1):
        if n_rels + 1 == 2 * c_id:
            continue
        ctzns[c_id-1]["relatives"] = [n_rels + 1 - c_id]

    return ctzns


@pytest.fixture()
def data(client):
    client.post(
        '/imports',
        data=json.dumps(
            {
                "citizens": gen_ctzns(3)
            }),
        content_type='application/json'
    )
