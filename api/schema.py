import datetime
import re
from enum import Enum
from typing import Any, Collection, Dict, List, MutableMapping, Optional, Set

from bson import ObjectId
from fastapi import HTTPException
from pydantic import (BaseModel, ConstrainedInt, ConstrainedStr, Field,
                      validator)


class MyBaseModel(BaseModel):
    """
    Переопределенный базовый класс для моделей, указывающий
    custom json encoders для даты и ObjectId.
    """
    class Config:
        json_encoders = {
            datetime.date: lambda v: v.strftime("%d.%m.%Y"),
            ObjectId: lambda v: str(v),
        }


class Gender(str, Enum):
    male = 'male'
    female = 'female'


class LenlimitedStr(ConstrainedStr):
    min_length = 1
    max_length = 256


class ContainAlnumStr(LenlimitedStr):
    """
    Непустая строка, содержащая хотя бы 1 букву или цифру.
    """
    regex = re.compile(r'(?!_)\w')


class NonNegativeInt(ConstrainedInt):
    ge = 0


class CitizenId(NonNegativeInt):
    pass


class BirthDate(datetime.date):
    """
    Дата рождения в формате ДД.ММ.ГГГГ (UTC +0). Должна быть меньше текущей
    даты.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.format
        yield cls.le_today

    @classmethod
    def format(cls, v):
        if isinstance(v, datetime.date):
            return v
        elif isinstance(v, str):
            return datetime.datetime.strptime(v, "%d.%m.%Y").date()

    @classmethod
    def le_today(cls, v: datetime.date):
        if not v <= datetime.date.today():
            raise ValueError('ensure date less than or equal today date')
        return v

    @classmethod  # pragma: no cover
    def __modify_schema__(cls, field_schema: Dict[str, Any]):
        field_schema.update({'example': '12.08.2007'})


class Citizen(MyBaseModel):
    citizen_id: CitizenId = Field(
        description="Уникальный идентификатор жителя, неотрицательное число."
    )
    town: ContainAlnumStr = Field(
        description="Название города. Непустая строка, содержащая хотя бы "
                    "1 букву или цифру, не более 256 символов."
    )
    street: ContainAlnumStr = Field(
        description="Название улицы. Непустая строка, содержащая хотя бы "
                    "1 букву или цифру, не более 256 символов."
    )
    building: ContainAlnumStr = Field(
        description="Номер дома, корпус и строение. Непустая строка, "
                    "содержащая хотя бы 1 букву или цифру, не более "
                    "256 символов."
    )
    name: LenlimitedStr = Field(
        description="Номер квартиры, неотрицательное число."
    )
    apartment: NonNegativeInt = Field(
        description="Непустая строка, не более 256 символов."
    )
    birth_date: BirthDate = Field(
        description="Дата рождения в формате ДД.ММ.ГГГГ (UTC +0). Должна быть "
                    "меньше текущей даты."
    )
    gender: Gender = Field(
        description="Значения male, female."
    )
    relatives: List[CitizenId] = Field(
        description="Ближайшие родственники, уникальные значения существующих "
                    "citizen_id жителей из этой же выгрузки."
    )


class Citizens(MyBaseModel):
    citizens: List[Citizen]


class Import(Citizens):
    @validator('citizens')
    def validate_unique(cls, citizens: Collection[Citizen]):
        """
        Проверяет что citizen_id жителей в наборе уникальны.
        """
        def unique_items(items: Collection[Any]) -> bool:
            return len(set(items)) == len(items)

        citizen_ids = tuple(citizen.citizen_id for citizen in citizens)

        if not unique_items(citizen_ids):
            raise ValueError('citizen_ids are not unique')

        return citizens

    @validator('citizens')
    def validate_relatives(cls, citizens: Set[Citizen]):
        """
        Проверяет, что указанные родственные свзяи для жителей в наборе
        валидны, то есть указывают на существующих в наборе жителей и указаны
        с каждой стороны.
        """
        relatives = {
            citizen.citizen_id: citizen.relatives
            for citizen in citizens
        }

        for citizen_id, relative_ids in relatives.items():
            for relative_id in relative_ids:
                if citizen_id not in relatives[relative_id]:
                    raise ValueError(
                        "citizens relatives are not bidirectional"
                    )
        return citizens


PrettyCitizens = MutableMapping[CitizenId, Citizen]


def to_pretty(citizens: List[Citizen]) -> PrettyCitizens:
    return {
        citizen.citizen_id: citizen for citizen in citizens
    }


def from_pretty(citizens: PrettyCitizens) -> List[Citizen]:
    return list(citizens.values())


class FieldsToPatch(MyBaseModel):
    town: Optional[ContainAlnumStr] = Field(
        description="Название города. Непустая строка, содержащая хотя бы "
                    "1 букву или цифру, не более 256 символов."
    )
    street: Optional[ContainAlnumStr] = Field(
        description="Название улицы. Непустая строка, содержащая хотя бы "
                    "1 букву или цифру, не более 256 символов."
    )
    building: Optional[ContainAlnumStr] = Field(
        description="Номер дома, корпус и строение. Непустая строка, "
                    "содержащая хотя бы 1 букву или цифру, не более "
                    "256 символов."
    )
    name: Optional[LenlimitedStr] = Field(
        description="Номер квартиры, неотрицательное число."
    )
    apartment: Optional[NonNegativeInt] = Field(
        description="Непустая строка, не более 256 символов."
    )
    birth_date: Optional[BirthDate] = Field(
        description="Дата рождения в формате ДД.ММ.ГГГГ (UTC +0). Должна быть "
                    "меньше текущей даты."
    )
    gender: Optional[Gender] = Field(
        description="Значения male, female."
    )
    relatives: Optional[List[CitizenId]] = Field(
        description="Ближайшие родственники, уникальные значения существующих "
                    "citizen_id жителей из этой же выгрузки."
    )


def update_relatives(
        new_relatives: List[CitizenId],
        old_relatives: List[CitizenId],
        citizens: PrettyCitizens,
        citizen_id: CitizenId
) -> PrettyCitizens:
    """
    Обновляет родственные свзяи, удаляя и добавляя их с обеих сторон.
    Возвращает только затронутых изменениями жителей.
    """
    relatives_to_add = set(new_relatives) - set(old_relatives)
    relatives_to_del = set(old_relatives) - set(new_relatives)

    different_citizens: PrettyCitizens = {}
    for relative_id in relatives_to_add | relatives_to_del:
        try:
            different_citizens[relative_id] = citizens[relative_id]

        except KeyError:
            raise ValueError(
                f'relative {relative_id} doesn\'t exist'
            )

    for relative_id in relatives_to_add:
        different_citizens[relative_id].relatives.append(citizen_id)

    for relative_id in relatives_to_del:
        different_citizens[relative_id].relatives.remove(citizen_id)

    return different_citizens


def update_citizens(
        citizens: PrettyCitizens,
        citizen_id: CitizenId,
        updated_fields: FieldsToPatch
) -> PrettyCitizens:
    """
    Обновляет данные жителей. Возвращает только данные, требующие обновления.
    """
    updated = updated_fields.dict(exclude_unset=True)
    if not updated:
        raise HTTPException(status_code=400, detail="Data must be not empty")
        # TODO: Instead move checks in FieldsToPatch

    try:
        citizen = citizens[citizen_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Citizen not found")

    new_relatives = updated.get("relatives", None)
    old_relatives = citizen.relatives

    different_citizens = update_relatives(
        new_relatives,
        old_relatives,
        citizens,
        citizen_id
    ) if (new_relatives is not None and
          new_relatives != old_relatives) else {}

    for key, value in updated.items():
        citizen.__setattr__(key, value)

    different_citizens[citizen_id] = citizen

    return different_citizens


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Not a valid ObjectId")

        return ObjectId(v)


class ImportResponse(MyBaseModel):
    class Data(MyBaseModel):
        import_id: ObjectIdStr

    data: Data


class GetResponse(MyBaseModel):
    data: List[Citizen]


class PatchResponse(MyBaseModel):
    data: Citizen


class BirthdaysResponse(MyBaseModel):
    class Year(MyBaseModel):
        class PresentsCounter(MyBaseModel):
            citizen_id: CitizenId
            presents: int

        month_1: List[PresentsCounter] = Field(alias='1')
        month_2: List[PresentsCounter] = Field(alias='2')
        month_3: List[PresentsCounter] = Field(alias='3')
        month_4: List[PresentsCounter] = Field(alias='4')
        month_5: List[PresentsCounter] = Field(alias='5')
        month_6: List[PresentsCounter] = Field(alias='6')
        month_7: List[PresentsCounter] = Field(alias='7')
        month_8: List[PresentsCounter] = Field(alias='8')
        month_9: List[PresentsCounter] = Field(alias='9')
        month_10: List[PresentsCounter] = Field(alias='10')
        month_11: List[PresentsCounter] = Field(alias='11')
        month_12: List[PresentsCounter] = Field(alias='12')

    data: Year


class AgeStatResponse(MyBaseModel):
    class TownStat(MyBaseModel):
        town: str
        p50: float
        p75: float
        p99: float

    data: List[TownStat]
