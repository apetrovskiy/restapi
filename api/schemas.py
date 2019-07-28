# -*- coding: utf-8 -*-

citizens_schema = {
    "type": "object",
    "properties": {
        "citizens": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "citizen_id": {"type": "integer"},
                    "name": {"type": "string"}
                },
                "required": ["citizen_id", "name"]
            },
            "minItems": 1,
            "uniqueItems": True
        }
    },
    "required": ["citizens"]
}
