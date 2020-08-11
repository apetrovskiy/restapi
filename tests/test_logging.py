# -*- coding: utf-8 -*-

import json

from _pytest.logging import LogCaptureFixture
from flask.testing import FlaskClient


def test_logging(client: FlaskClient, caplog: LogCaptureFixture) -> None:
    response = client.get('/exc')

    assert response.status_code == 500
    assert json.loads(response.data) == {
        "error": 500,
        "description": "Internal Server Error"
    }

    assert any(record.levelname == "ERROR" for record in caplog.records)
    assert "division by zero" in caplog.text
