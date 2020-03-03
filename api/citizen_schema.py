# -*- coding: utf-8 -*-
import datetime
from typing import (
    Any, Mapping, Collection, Iterable, MutableMapping, MutableSequence
)

from marshmallow import (
    Schema, fields, validate, post_load, RAISE, ValidationError
)

__all__ = ["NotFound", "ValidationError", "validate_import_citizens",
           "update_citizens", "CitizenSchema", "unique_items", "Citizen"]


def isalnum(s: str) -> bool:
    return any(map(str.isalnum, s))


def unique_items(x: Collection[int]) -> bool:
    return len(set(x)) == len(x)


class Citizen:
    def __init__(self,
                 citizen_id: int,
                 town: str,
                 street: str,
                 building: str,
                 name: str,
                 apartment: str,
                 birth_date: datetime.date,
                 gender: str,
                 relatives: MutableSequence[int]) -> None:
        self.citizen_id = citizen_id
        self.town = town
        self.street = street
        self.building = building
        self.name = name
        self.apartment = apartment
        self.birth_date = birth_date
        self.gender = gender
        self.relatives = relatives


class CitizenSchema(Schema):
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

    @post_load
    def make_citizen(self, data: Any, **kwargs: Any) -> Any:
        if not self.partial:
            return Citizen(**data)
        else:
            return data


class NotFound(Exception):
    """При вызове методов для несуществующих import_id или citizen_id"""

    pass


def validate_import_citizens(
    citizens: Any
) -> Mapping[int, Citizen]:
    citizens = CitizenSchema(unknown=RAISE, many=True).load(citizens)
    citizen_ids = tuple(citizen.citizen_id for citizen in citizens)

    if not unique_items(citizen_ids):
        raise ValidationError('citizen_ids are not unique')

    relatives = {citizen.citizen_id: citizen.relatives for citizen in citizens}

    for citizen_id, relative_ids in relatives.items():
        for relative_id in relative_ids:
            if citizen_id not in relatives[relative_id]:
                raise ValidationError(
                    "citizens relatives are not bidirectional"
                )

    return {citizen.citizen_id: citizen for citizen in citizens}


def update_relatives(
        new_relatives: Iterable[int],
        old_relatives: Iterable[int],
        citizens: Mapping[int, Citizen],
        citizen_id: int
) -> MutableMapping[int, Citizen]:
    """Возвращает данные горожан, требующие обновления"""
    relatives_to_add = set(new_relatives) - set(old_relatives)
    relatives_to_del = set(old_relatives) - set(new_relatives)

    different_citizens: MutableMapping[int, Citizen] = {}
    for relative_id in relatives_to_add | relatives_to_del:
        try:
            different_citizens[relative_id] = citizens[relative_id]

        except KeyError:
            raise ValidationError(
                f'relative {relative_id} doesn\'t exist'
            )

    for relative_id in relatives_to_add:
        different_citizens[relative_id].relatives.append(citizen_id)

    for relative_id in relatives_to_del:
        different_citizens[relative_id].relatives.remove(citizen_id)

    return different_citizens


def update_citizens(
        citizens: Mapping[int, Citizen],
        citizen_id: int,
        updated_fields: Any
) -> Mapping[int, Citizen]:
    """Обновляет данные жителя. Возвращает только данные,
    требующие обновления"""

    if not updated_fields:
        raise ValidationError('Data must be not empty')

    updated_fields = CitizenSchema(
        exclude=["citizen_id"],
        unknown=RAISE,
        partial=True
    ).load(updated_fields)

    try:
        citizen = citizens[citizen_id]
    except KeyError:
        raise NotFound('citizen doesn\'t exist')

    new_relatives = updated_fields.get("relatives", None)
    old_relatives = citizen.relatives

    different_citizens = update_relatives(
            new_relatives,
            old_relatives,
            citizens,
            citizen_id
    ) if (new_relatives is not None and
          new_relatives != old_relatives) else {}

    for key, value in updated_fields.items():
        citizen.__setattr__(key, value)

    different_citizens[citizen_id] = citizen

    return different_citizens
