# -*- coding: utf-8 -*-
"""
    Обработчики логики
    ~~~~~~~~~~~~~~~~~~

    .. POST /imports
        post_imp()

    .. PATCH /imports/$import_id/citizens/$citizen_id
        patch_ctzn(import_id, citizen_id)

    .. GET /imports/$import_id/citizens
        get_ctzns(import_id)

    .. GET /imports/$import_id/citizens/birthdays
        get_birthdays(import_id)

    .. GET /imports/$import_id/towns/stat/percentile/age
        get_age_stat(import_id)

"""

from datetime import datetime, date

from flask import Blueprint, request, jsonify, abort
from numpy import percentile

from api.orm import CtznsDAO, NotFound, ValidationError

__all__ = ["bp"]

bp = Blueprint('controllers', __name__)
_db = CtznsDAO()


@bp.route('/imports', methods=['POST'])
def post_imp():
    """Принимает на вход набор с данными о жителях в формате json и
    сохраняет его с уникальным идентификатором import_id.

    """

    try:
        imp_id = _db.create(request.get_json())

    except ValidationError as ve:
        abort(400, str(ve))

    return jsonify({"data": {"import_id": imp_id}}), 201


@bp.route('/imports/<int:imp_id>/citizens/<int:ctzn_id>', methods=['PATCH'])
def patch_ctzn(imp_id, ctzn_id):
    """Изменяет информацию о жителе в указанном наборе данных."""

    new_fields = request.get_json()
    try:
        ctzn = _db.update(imp_id, ctzn_id, new_fields)

    except NotFound as ve:
        abort(404, str(ve))

    except ValidationError as ve:
        abort(400, str(ve))

    return jsonify({"data": ctzn}), 200


@bp.route('/imports/<int:imp_id>/citizens', methods=['GET'])
def get_ctzns(imp_id: int):
    """Возвращает список всех жителей для указанного набора данных."""

    try:
        ctzns = _db.read(imp_id)

    except NotFound as ve:
        abort(404, str(ve))

    ctzns = list(ctzns.values())

    return jsonify({"data": ctzns}), 200


@bp.route('/imports/<int:imp_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(imp_id: int):
    """Возвращает жителей и количество подарков, которые они будут
    покупать своим ближайшим родственникам (1-го порядка),
    сгруппированных по месяцам из указанного набора данных.

    """

    try:
        ctzns = _db.read(imp_id)

    except NotFound as ve:
        abort(404, str(ve))

    months = dict(
        (str(i), {})
        for i in range(1, 12 + 1)
    )

    for ctzn_id, ctzn in ctzns.items():
        for rel_id in ctzn["relatives"]:
            rel = ctzns[str(rel_id)]
            month = rel["birth_date"].split('.')[1]
            month = month.lstrip("0")
            no_presents = {
                "citizen_id": int(ctzn_id), "presents": 0
            }
            c = months[month].get(int(ctzn_id), no_presents)
            c["presents"] += 1
            months[month][int(ctzn_id)] = c

    months = dict(
        (
            str(i),
            list(months[str(i)].values())
        )
        for i in range(1, 12 + 1)
    )

    return jsonify({"data": months}), 200


@bp.route('/imports/<int:imp_id>/towns/stat/percentile/age', methods=['GET'])
def get_age_stat(imp_id: int):
    """Возвращает статистику по городам для указанного набора данных в
    разрезе возраста (полных лет) жителей: p50, p75, p99, где число -
    это значение перцентиля.

    Для даты удаляются ведущие и завершающие пробелы.

    Колличество полных лет учитывает был ли уже день рождения в этом
    году или нет.

    """

    try:
        ctzns = _db.read(imp_id)

    except NotFound as ve:
        abort(404, str(ve))

    towns = {}

    for ctzn in ctzns.values():
        birth_date = datetime.strptime(ctzn["birth_date"].strip(), "%d.%m.%Y")
        today = date.today()
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            was_already = False
        else:
            was_already = True
        age = today.year - birth_date.year - int(not was_already)

        town = ctzn["town"]
        ages = towns.get(town, [])
        ages.append(age)
        towns[town] = ages

    stats = []

    for town in towns:
        stat = {}
        stat["town"] = town

        for pv in (50, 75, 99):
            stat["p" + str(pv)] = round(
                percentile(towns[town], pv, interpolation='linear'), 2
            )

        stats.append(stat)

    return jsonify({"data": stats}), 200
