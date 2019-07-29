# -*- coding: utf-8 -*-

from jsonschema import ValidationError

imp_schema = {
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


def get_ctzn(id_: int, ctzns: list):
    for ctzn in ctzns:
        if ctzn["citizen_id"] == id_:
            return ctzn

    return None


def validate_relatives(ctzn: dict, ctzns: list):
    for rel_id in ctzn["relatives"]:
        rel = get_ctzn(rel_id, ctzns)
        if ctzn["citizen_id"] not in rel["relatives"]:
            raise ValidationError("Родственные связи двусторонние")


def validate_unique_id(c_id: int, c_ids: set):
    if c_id in c_ids:
        raise ValidationError("Уникальный идентификатор жителя")
    else:
        c_ids.add(c_id)


ctzn_schema = {
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
    "additionalProperties": False,
}
