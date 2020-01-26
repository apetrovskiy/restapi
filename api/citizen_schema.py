# -*- coding: utf-8 -*-

import datetime
from typing import List

from marshmallow import Schema, fields, validate

__all__ = ["Citizen"]


def isalnum(s: str) -> bool:
    return any(map(str.isalnum, s))


def unique_items(x: List[int]) -> bool:
    return len(set(x)) == len(x)


class Citizen(Schema):
    citizen_id = fields.Int(
        validate=validate.Range(
            min=0,
            min_inclusive=True),
        required=True)
    town = fields.Str(
        validate=(
            isalnum,
            validate.Length(min=1, max=256)),
        required=True)
    street = fields.Str(
        validate=(
            isalnum,
            validate.Length(min=1, max=256)),
        required=True)
    building = fields.Str(
        validate=(
            isalnum,
            validate.Length(min=1, max=256)),
        required=True)
    name = fields.Str(
        validate=validate.Length(min=1, max=256),
        required=True)
    apartment = fields.Int(
        validate=validate.Range(
            min=0,
            min_inclusive=True),
        required=True)
    birth_date = fields.Date(
        format='%d.%m.%Y',
        validate=validate.Range(
            max=datetime.date.today(),
            max_inclusive=True),
        required=True)
    gender = fields.Str(
        validate=validate.OneOf(('male', 'female')),
        required=True)
    relatives = fields.List(
        citizen_id,
        validate=unique_items,
        required=True
    )
