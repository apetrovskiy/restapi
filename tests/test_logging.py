# -*- coding: utf-8 -*-

import json


def test_logging(client, caplog):
    response = client.get('/exc')

    assert response.status_code == 500
    assert json.loads(response.data) == {
        "error": 500,
        "description": "Internal Server Error"
    }

    assert any(record.levelname == "ERROR" for record in caplog.records)
    assert "division by zero" in caplog.text
