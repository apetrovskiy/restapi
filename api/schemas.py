# -*- coding: utf-8 -*-

import re
from jsonschema import ValidationError

citizens_schema = {
    "type": "object",
    "properties": {
        "citizens": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "citizen_id": {"type": "integer", "minimum": 1},
                    "town": {"type": "string", "minLength": 1},
                    "street": {"type": "string", "minLength": 1},
                    "building": {"type": "string", "minLength": 1},
                    "apartment": {"type": "integer", "minimum": 1},
                    "name": {"type": "string", "minLength": 1},
                    "birth_date": {"type": "string", "minLength": 1},
                    "gender": {"type": "string", "minLength": 1},
                    "relatives": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1}
                    }
                },
                "required": [
                    "citizen_id",
                    "town",
                    "street",
                    "building",
                    "apartment",
                    "name",
                    "birth_date",
                    "gender",
                    "relatives"
                ],
                "additionalProperties": False,
            },
            "minItems": 1,
            "uniqueItems": True
        }
    },
    "required": ["citizens"],
    "additionalProperties": False
}


def validate_birth_date(birth_date):
    if not re.match(r"\s*\d{2}\.\d{2}\.\d{4}\s*", birth_date):
        raise ValidationError("Дата рождения в формате ДД.ММ.ГГГГ")


def validate_gender(gender):
    if gender not in ['male', 'female']:
        raise ValidationError("Значения male, female")


def validate_relatives(citizen, citizens):
    for c_id in citizen["relatives"]:
        e = next((ctz for ctz in citizens if ctz['citizen_id'] == c_id), None)
        if citizen["citizen_id"] not in e["relatives"]:
            raise ValidationError("Родственные связи двусторонние")
