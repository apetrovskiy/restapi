# -*- coding: utf-8 -*-

import json


def test_500(client):
    response = client.get('/exc')
    assert response.status_code == 500
    assert json.loads(response.data) == {
        "error": "Internal Server Error"
    }

    with open('teststemp/logs/api.log', 'r') as log:
        assert "ZeroDivisionError: some text" in log.read()
