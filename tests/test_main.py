# -*- coding: utf-8 -*-

import json
from typing import Iterable

from bson import ObjectId
from pytest import fixture

from tests import import_id, Citizen_s


def test_import_citizens(client: fixture, data3: Iterable[Citizen_s]) -> None:
    post_response = client.post(
        '/imports',
        data=json.dumps({
            "citizens": data3
        }),
        content_type='application/json'
    )

    assert post_response.status_code == 201
    assert ObjectId.is_valid(import_id(post_response))


def test_patch_citizen(client: fixture, data3: Iterable[Citizen_s]) -> None:
    post_response = client.post(
        '/imports',
        data=json.dumps({
            "citizens": data3
        }),
        content_type='application/json'
    )

    patch_response = client.patch(
        f'/imports/{import_id(post_response)}/citizens/3',
        data=json.dumps(
            {
                "name": "Иванова Мария Леонидовна",
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "relatives": [1]
            }
        ),
        content_type='application/json'
    )
    assert patch_response.status_code == 200
    assert json.loads(patch_response.data).get("data", {}) == {
        "citizen_id": 3,
        "town": "Москва",
        "street": "Льва Толстого",
        "building": "16к7стр5",
        "apartment": 7,
        "name": "Иванова Мария Леонидовна",
        "birth_date": "23.11.1986",
        "gender": "female",
        "relatives": [1]

    }


def test_get_citizens(client: fixture, data3: Iterable[Citizen_s]) -> None:
    post_response = client.post(
        '/imports',
        data=json.dumps({
            "citizens": data3
        }),
        content_type='application/json'
    )

    get_response = client.get(
        f'/imports/{import_id(post_response)}/citizens'
    )
    assert get_response.status_code == 200
    assert json.loads(get_response.data) == {
        "data": data3
    }


def test_get_birthdays(client: fixture, data3: Iterable[Citizen_s]) -> None:
    post_response = client.post(
        '/imports',
        data=json.dumps({
            "citizens": data3
        }),
        content_type='application/json'
    )

    get_response = client.get(
        f'/imports/{import_id(post_response)}/citizens/birthdays'
    )
    assert get_response.status_code == 200
    assert json.loads(get_response.data) == {
        "data": {
            "1": [],
            "2": [],
            "3": [],
            "4": [{"citizen_id": 1, "presents": 1}],
            "5": [],
            "6": [],
            "7": [],
            "8": [],
            "9": [],
            "10": [],
            "11": [],
            "12": [{"citizen_id": 2, "presents": 1}]
        }
    }


def test_get_age_stat(client: fixture, data3: Iterable[Citizen_s]) -> None:
    post_response = client.post(
        '/imports',
        data=json.dumps({
            "citizens": data3
        }),
        content_type='application/json'
    )

    get_response = client.get(
        f'/imports/{import_id(post_response)}/towns/stat/percentile/age'
    )

    assert get_response.status_code == 200
    assert json.loads(get_response.data) == {
        "data": [
            {
                "p50": 27.5,
                "p75": 30.25,
                "p99": 32.89,
                "town": "Москва"
            },
            {
                "p50": 33.0,
                "p75": 33.0,
                "p99": 33.0,
                "town": "Керчь"
            }
        ]
    }
