from bson import ObjectId
from fastapi.testclient import TestClient

from api import app
from tests import import_id

client = TestClient(app)


def test_import_citizens(post):
    assert post.status_code == 201
    assert ObjectId.is_valid(import_id(post))


def test_patch_citizen(post):
    patch_response = client.patch(
        f'/imports/{import_id(post)}/citizens/3',
        json={
            "name": "Иванова Мария Леонидовна",
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "relatives": [1]
        }
    )
    assert patch_response.status_code == 200
    assert patch_response.json().get("data", {}) == {
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


def test_get_citizens(post, import_example):
    get_response = client.get(
        f'/imports/{import_id(post)}/citizens'
    )
    assert get_response.status_code == 200
    assert get_response.json()["data"] == import_example["citizens"]


def test_get_birthdays(post):
    get_response = client.get(
        f'/imports/{import_id(post)}/citizens/birthdays'
    )
    assert get_response.status_code == 200
    assert get_response.json() == {
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


def test_get_age_stat(post):
    get_response = client.get(
        f'/imports/{import_id(post)}/towns/stat/percentile/age'
    )

    assert get_response.status_code == 200
    for key in ("p50",
                "p75",
                "p99",
                "town"):
        assert key in get_response.json()["data"][0]
