from fastapi import APIRouter

from api.functions import calc_age_by_towns, calc_birthdays
from api.mongo_orm import create, read, update
from api.schema import (AgeStatResponse, BirthdaysResponse, CitizenId,
                        FieldsToPatch, GetResponse, Import, ImportResponse,
                        ObjectIdStr, PatchResponse, to_pretty, update_citizens)

router = APIRouter()


@router.post(
    "/",
    response_model=ImportResponse,
    status_code=201,
    tags=['imports']
)
async def import_citizens(import_: Import):
    """
    Принимает на вход набор с данными о жителях в формате json и
    сохраняет его с уникальным идентификатором import_id.
    """

    import_id = create(import_)

    return ImportResponse(
        data=ImportResponse.Data(
            import_id=import_id
        )
    )


@router.patch(
    "/{import_id}/citizens/{citizen_id}",
    response_model=PatchResponse,
    tags=['imports']
)
async def patch_citizen(
        import_id: ObjectIdStr,
        citizen_id: CitizenId,
        fields: FieldsToPatch
):
    """
    Изменяет информацию о жителе в указанном наборе данных.
    """

    import_ = read(import_id)
    citizens = to_pretty(import_.citizens)
    different_citizens = update_citizens(citizens, citizen_id, fields)
    update(import_id, different_citizens)

    return PatchResponse(data=different_citizens[citizen_id])


@router.get(
    "/{import_id}/citizens",
    response_model=GetResponse,
    tags=['imports']
)
async def get_citizens(import_id: ObjectIdStr):
    """
    Возвращает список всех жителей для указанного набора данных.
    """

    import_ = read(import_id)

    return GetResponse(data=import_.citizens)


@router.get(
    "/{import_id}/citizens/birthdays",
    response_model=BirthdaysResponse,
    tags=['imports']
)
async def get_birthdays(import_id: ObjectIdStr):
    """
    Возвращает жителей и количество подарков, которые они будут
    покупать своим ближайшим родственникам (1-го порядка),
    сгруппированных по месяцам из указанного набора данных.
    """

    import_ = read(import_id)
    citizens = to_pretty(import_.citizens)

    return BirthdaysResponse(
        data=calc_birthdays(citizens)
    )


@router.get(
    "/{import_id}/towns/stat/percentile/age",
    response_model=AgeStatResponse,
    tags=['imports']
)
def get_age_stat(import_id: ObjectIdStr):
    """
    Возвращает статистику по городам для указанного набора данных в
    разрезе возраста (полных лет) жителей: p50, p75, p99, где число -
    это значение перцентиля.
    """
    import_ = read(import_id)
    citizens = to_pretty(import_.citizens)

    return AgeStatResponse(data=calc_age_by_towns(citizens))
