from bson import ObjectId
from fastapi.testclient import TestClient

from api import app
from tests import import_id

client = TestClient(app)


def test_no_import():
    random_id = str(ObjectId())
    get_response = client.get(
        f'/imports/{random_id}/citizens'
    )
    assert get_response.status_code == 404


def test_empty_patch_data(post):
    patch_response = client.patch(
        f'/imports/{import_id(post)}/citizens/3',
        json={}
    )
    assert patch_response.status_code == 400


def test_no_citizen(post):
    not_existed_citizen_id = 100

    patch_response = client.patch(
        f'/imports/{import_id(post)}/citizens/{not_existed_citizen_id}',
        json={
            "name": "Иванова Мария Леонидовна"
        }
    )
    assert patch_response.status_code == 404


def test_invalid_import_id():
    not_valid_object_id = 1
    get_response = client.get(
        f'/imports/{not_valid_object_id}/citizens'
    )
    assert get_response.status_code == 422
