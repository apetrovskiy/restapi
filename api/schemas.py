# -*- coding: utf-8 -*-

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

ctzn_schema = {
    "type": "object",
    "properties": {
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
    "minProperties": 1,
    "additionalProperties": False,
}
