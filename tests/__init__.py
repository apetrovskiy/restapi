# -*- coding: utf-8 -*-

import json
from typing import Iterable, Mapping, Union, MutableMapping

from bson import ObjectId
from flask.wrappers import ResponseBase

from api.citizen_schema import Citizen, update_relatives

__all__ = ["import_id", "change_relatives_to", "Citizen_s"]

Citizen_s = MutableMapping[str, Union[int, str, Iterable[int]]]


def import_id(post_response: ResponseBase) -> ObjectId:
    return json.loads(post_response.data).get("data", {}).get("import_id", "")


def change_relatives_to(
        data3d: Mapping[int, Citizen],
        citizen_id: int,
        relatives: Iterable[int]
) -> Mapping[int, Citizen]:
    different_citizens = update_relatives(
        relatives, data3d[citizen_id].relatives, data3d, citizen_id
    )

    return different_citizens
