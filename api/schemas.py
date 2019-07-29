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
                    "birth_date": {
                        "type": "string",
                        "pattern": "[0-9]{2}\\.(0[1-9]|10|11|12)\\.[0-9]{4}"
                        },
                    "gender": {
                        "type": "string",
                        "enum": ["male", "female"]
                        },
                    "relatives": {
                        "type": "array",
                        "uniqueItems": True,
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


def validate_relatives(citizen, citizens):
    for rel_id in citizen["relatives"]:
        ctz = next((ctz for ctz in citizens if ctz['citizen_id'] == rel_id), None)
        if citizen["citizen_id"] not in ctz["relatives"]:
            raise ValidationError("Родственные связи двусторонние")


def validate_unique_citizen_id(citizen, c_ids):
    if citizen['citizen_id'] in c_ids:
        raise ValidationError("Уникальный идентификатор жителя")
    else:
        c_ids.append(citizen['citizen_id'])


patch_citizen_schema = {
    "type": "object",
    "properties": {
        "citizen_id": {"type": "integer", "minimum": 1},
        "town": {"type": "string", "minLength": 1},
        "street": {"type": "string", "minLength": 1},
        "building": {"type": "string", "minLength": 1},
        "apartment": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1},
        "birth_date": {
            "type": "string",
            "pattern": "[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}"
            },
        "gender": {
            "type": "string",
            "enum": ["male", "female"]
            },
        "relatives": {
            "type": "array",
            "uniqueItems": True,
            "items": {"type": "integer", "minimum": 1}
        }
    },
    "additionalProperties": False,
}
