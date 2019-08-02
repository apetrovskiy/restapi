# -*- coding: utf-8 -*-

import json


def test_no_import(client, post):
    response = client.get('/imports/2/citizens')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "error": "Not found"
    }


def test_expected(client, post):
    response = client.get('/imports/1/citizens/birthdays')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "data": {
            "1": [],
            "2": [],
            "3": [],
            "4": [{
                "citizen_id": 1,
                "presents": 1,
                 }],
            "5": [],
            "6": [],
            "7": [],
            "8": [],
            "9": [],
            "10": [],
            "11": [],
            "12": [{
                    "citizen_id": 2,
                    "presents": 1
                }]
            }
        }
