# -*- coding: utf-8 -*-
from typing import Mapping, Sequence

import pytest
from marshmallow import ValidationError

from api.citizen_schema import validate_import_citizens, update_citizens
from tests import Citizen_s


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
    }
])
def test_fields_errors(data: Mapping[str, Sequence[Citizen_s]]) -> None:
    with pytest.raises(ValidationError):
        validate_import_citizens(data)

    fields = data["citizens"][0]
    fields.pop("citizen_id")

    with pytest.raises(ValidationError):
        # Препдолагается, что функция update_citizens сначала проверяет fields
        update_citizens({}, 1, fields)


@pytest.mark.parametrize("data", [
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
def test_relatives_and_ids_errors(
        data: Mapping[str, Sequence[Citizen_s]]
) -> None:
    with pytest.raises(ValidationError):
        validate_import_citizens(data)
