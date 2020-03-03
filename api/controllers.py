# -*- coding: utf-8 -*-
"""
    Обработчики логики
    ~~~~~~~~~~~~~~~~~~

    .. POST /imports
        import_citizens()

    .. PATCH /imports/$import_id/citizens/$citizen_id
        patch_citizen(import_id: str, citizen_id: int)

    .. GET /imports/$import_id/citizens
        get_citizen(import_id: str)

    .. GET /imports/$import_id/citizens/birthdays
        get_birthdays(import_id: str)

    .. GET /imports/$import_id/towns/stat/percentile/age
        get_age_stat(import_id: str)

"""
from typing import Any

from flask import Blueprint, request, jsonify, abort

from api.mongo_orm import create, read, update, ConnectionFailure
from api.functions import calc_birthdays, calc_age_by_towns
from api.citizen_schema import (
    NotFound, ValidationError, validate_import_citizens, update_citizens,
    CitizenSchema
)

__all__ = ["bp"]

bp = Blueprint('controllers', __name__)


@bp.route('', methods=['POST'])
def import_citizens() -> Any:
    """Принимает на вход набор с данными о жителях в формате json и
    сохраняет его с уникальным идентификатором import_id.

    """
    try:
        citizens_data = request.get_json().get("citizens")
    except KeyError:
        raise abort(400, 'Import must contain "citizens" field')

    try:
        citizens_data = validate_import_citizens(citizens_data)

    except ValidationError as ve:
        return abort(400, str(ve))

    try:
        import_id = create(citizens_data)
    except ConnectionFailure:
        return abort(500)

    response = {
        "data": {
            "import_id": import_id,
        }
    }

    return jsonify(response), 201


@bp.route('/<string:import_id>/citizens/<int:citizen_id>', methods=['PATCH'])
def patch_citizen(import_id: str, citizen_id: int) -> Any:
    """Изменяет информацию о жителе в указанном наборе данных."""

    fields = request.get_json()
    try:
        citizens = read(import_id)

    except ConnectionFailure:
        return abort(500)

    except NotFound as nf:
        return abort(404, str(nf))

    try:
        different_citizens = update_citizens(citizens, citizen_id, fields)

    except NotFound as nf:
        return abort(404, str(nf))

    except ValidationError as ve:
        return abort(400, str(ve))

    try:
        update(import_id, different_citizens)
    except ConnectionFailure:
        return abort(500)

    response = {
        "data": CitizenSchema().dump(different_citizens[citizen_id])
    }

    return jsonify(response), 200


@bp.route('/<string:import_id>/citizens', methods=['GET'])
def get_citizens(import_id: str) -> Any:
    """Возвращает список всех жителей для указанного набора данных."""

    try:
        citizens_data = read(import_id)

    except ConnectionFailure:
        return abort(500)

    except NotFound as nf:
        return abort(404, str(nf))

    response = {
        "data": CitizenSchema().dump(citizens_data.values(), many=True)
    }

    return jsonify(response), 200


@bp.route('/<string:import_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(import_id: str) -> Any:
    """Возвращает жителей и количество подарков, которые они будут
    покупать своим ближайшим родственникам (1-го порядка),
    сгруппированных по месяцам из указанного набора данных.

    """

    try:
        citizens_data = read(import_id)

    except ConnectionFailure:
        return abort(500)

    except NotFound as nf:
        return abort(404, str(nf))

    response = {
        "data": calc_birthdays(citizens_data)
    }

    return jsonify(response), 200


@bp.route('/<string:import_id>/towns/stat/percentile/age', methods=['GET'])
def get_age_stat(import_id: str) -> Any:
    """Возвращает статистику по городам для указанного набора данных в
    разрезе возраста (полных лет) жителей: p50, p75, p99, где число -
    это значение перцентиля.

    Колличество полных лет учитывает был ли уже день рождения в этом
    году или нет.

    """

    try:
        citizens_data = read(import_id)

    except ConnectionFailure:
        return abort(500)

    except NotFound as nf:
        return abort(404, str(nf))

    response = {
        "data": calc_age_by_towns(citizens_data)
    }

    return jsonify(response), 200
