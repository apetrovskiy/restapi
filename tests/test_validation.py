import pytest
from pydantic import ValidationError

from api.schema import Import


@pytest.mark.parametrize("data", [
    {
        "citizens": [
            {
                "citizen_id": 1,
                "town": "М" * 257,  # Length
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Иван Иванович",
                "birth_date": "01.02.1986",
                "gender": "male",
                "relatives": []
            }
        ]
    },
    {
        "citizens": [
            {
                "citizen_id": 1,
                "town": "_",  # Not alnum
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Иван Иванович",
                "birth_date": "01.01.1900",
                "gender": "male",
                "relatives": []
            }
        ]
    },
    {
        "citizens": [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Иван Иванович",
                "birth_date": "31.02.1986",  # Invalid day and month pair
                "gender": "male",
                "relatives": []
            }
        ]
    },
    {
        "citizens": [
            {
                "citizen_id": 1,
                "town": "Мосвка",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Иван Иванович",
                "birth_date": "01.01.9000",  # Invalid year
                "gender": "male",
                "relatives": []
            }
        ]
    },
    {
        "citizens": [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Иван Иванович",
                "birth_date": "26.13.1986",  # Invalid month
                "gender": "male",
                "relatives": []
            }
        ]
    },
    {
        "citizens": [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Иван Иванович",
                "birth_date": "26.13.1986",
                "gender": "male",
                "relatives": [100]  # Relative does not exist in import
            }
        ]
    },
    {
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
                "relatives": []  # Invalid relatives
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
            }
        ]
    },
    {
        "citizens": [
            {
                "citizen_id": 1,  # Not unique citizen ids
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
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "17.04.1997",
                "gender": "male",
                "relatives": [1]
            }
        ]
    }
])
def test_validation(data) -> None:
    with pytest.raises(ValidationError):
        Import(**data)
