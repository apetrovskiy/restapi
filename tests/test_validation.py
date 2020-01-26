# -*- coding: utf-8 -*-

import pytest
from marshmallow import ValidationError

from api.validation import validate_import_citizens, validate_patch_citizen


@pytest.mark.parametrize("data", [
    {
        "citizens": [
            {
                "citizen_id": 1,
                "town": "М" * 257,
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
                "town": "_",
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
                "birth_date": "31.02.1986",
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
                "birth_date": "01.01.9000",
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
                "relatives": []
            }
        ]
    }
])
def test_fields_errors(data: dict):
    with pytest.raises(ValidationError):
        validate_import_citizens(data)

    flds = data["citizens"][0]
    ctzn_id = flds.copy().pop("citizen_id")
    data = {str(ctzn_id): flds}
    with pytest.raises(ValidationError):
        validate_patch_citizen(data, ctzn_id, flds)


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
                "relatives": []
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
def test_relatives_and_ids_errors(data: dict):
    with pytest.raises(ValidationError):
        validate_import_citizens(data)
