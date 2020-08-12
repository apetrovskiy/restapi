import pytest
from fastapi.testclient import TestClient

from api import app
from api.schema import Citizens, to_pretty

client = TestClient(app)


@pytest.fixture
def import_example():
    return {
        "citizens": [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Иван Иванович",
                "birth_date": "26.12.1986",
                "gender": "male",
                "relatives": [2]
            },
            {
                "citizen_id": 2,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "17.04.1997",
                "gender": "male",
                "relatives": [1]
            },
            {
                "citizen_id": 3,
                "town": "Керчь",
                "street": "Иосифа Бродского",
                "building": "2",
                "apartment": 11,
                "name": "Романова Мария Леонидовна",
                "birth_date": "23.11.1986",
                "gender": "female",
                "relatives": []
            }
        ]
    }


@pytest.fixture
def post(import_example):
    return client.post(
        "/imports/",
        json=import_example
    )


@pytest.fixture
def pretty_citizens(import_example):
    return to_pretty(Citizens(**import_example).citizens)
