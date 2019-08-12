# -*- coding: utf-8 -*-
"""
    Обработчики логики
    ~~~~~~~~~~~~~~~~~~

    .. POST /imports
        post_imp()

    .. PATCH /imports/$import_id/citizens/$citizen_id
        patch_ctzn(import_id: int, citizen_id: int)

    .. GET /imports/$import_id/citizens
        get_ctzns(import_id: int)

    .. GET /imports/$import_id/citizens/birthdays
        get_birthdays(import_id: int)

    .. GET /imports/$import_id/towns/stat/percentile/age
        get_age_stat(import_id: int)


    Обработчики ошибок
    ~~~~~~~~~~~~~~~~~~

    .. 400
        bad_request(ex)

"""

import json
from datetime import datetime, date

import fastjsonschema
from fastjsonschema import JsonSchemaException
from flask import Blueprint, request, jsonify, abort
from numpy import percentile

from api.db import get_db

bp = Blueprint('controllers', __name__)

# Позволяет использовать локальные ссылки в json-схемах
# См. fastjsonschema/ref_resolver.py::resolve_remote()
# Неуказанный (пустой) протокол в json-схеме вызывает lambda-функцию
__locrefhandler = {"": lambda file: json.load(open('api/schemas/' + file))}


@bp.route('/imports', methods=['POST'])
def post_imp():
    """Принимает на вход набор с данными о жителях в формате json и сохраняет
    его с уникальным идентификатором import_id.

    Валидация:
    .. Поля - json-схема
    .. Дата - datetime.date
    .. ID   - ключи словаря
    .. Родственники - перебор в цикле
    """
    imp = request.get_json()
    try:
        schema = json.load(open('api/schemas/imp.json'))
        fastjsonschema.validate(schema, imp)

        # Проверка жителей отдельной схемой в цикле идёт быстрее
        ctzns = {}
        schema = json.load(open('api/schemas/crt_ctzn.json'))
        validator = fastjsonschema.compile(schema, handlers=__locrefhandler)

        for ctzn in imp["citizens"]:
            validator(ctzn)
            ctzn_id = ctzn["citizen_id"]

            if str(ctzn_id) in ctzns.keys():
                raise JsonSchemaException('citizen_ids are not unique')

            dd, mm, yyyy = map(int, ctzn["birth_date"].split('.'))
            try:
                date(yyyy, mm, dd)
            except ValueError as ve:
                raise JsonSchemaException(ve)

            ctzns[str(ctzn_id)] = ctzn

        for ctzn_id, ctzn in ctzns.items():
            for rel_id in ctzn["relatives"]:
                rel = ctzns[str(rel_id)]

                if int(ctzn_id) not in rel["relatives"]:
                    raise JsonSchemaException(
                        "citizens relatives are not bidirectional"
                    )

    except JsonSchemaException as ve:
        abort(400, str(ve))

    db = get_db()
    imp_id = db.imports.count_documents({}) + 1
    ctzns["_id"] = imp_id
    db.imports.insert_one(ctzns)

    return jsonify({"data": {"import_id": imp_id}}), 201


@bp.route('/imports/<int:imp_id>/citizens/<int:ctzn_id>',
          methods=['PATCH'])
def patch_ctzn(imp_id: int, ctzn_id: int):
    """Изменяет информацию о жителе в указанном наборе данных.

    Валидация:
    .. Поля - json-схема
    .. Дата - datetime.date
    .. Родственники - перебор в цикле

    Жители, данные которых изменились, перезаписываются полностью.

    Для связей вычисляются удаляемые и добавляемые.
    Изменение происходит перебором в цикле.
    """
    new_fields = request.get_json()
    schema = json.load(open('api/schemas/upd_ctzn.json'))
    validator = fastjsonschema.compile(schema, handlers=__locrefhandler)
    try:
        validator(new_fields)

        if "birth_date" in new_fields:
            dd, mm, yyyy = map(int, new_fields["birth_date"].split('.'))
            try:
                date(yyyy, mm, dd)
            except ValueError as ve:
                raise JsonSchemaException(ve)

    except JsonSchemaException as ve:
        abort(400, str(ve))

    db = get_db()
    ctzns = db.imports.find_one({"_id": imp_id})
    ctzns_for_upd = {}

    if ctzns is None:
        abort(404, 'import doesn\'t exist')
    if not str(ctzn_id) in ctzns:
        abort(404, 'citizen doesn\'t exist')

    ctzn = ctzns[str(ctzn_id)]

    if "relatives" in new_fields:
        prev_rels = ctzn["relatives"]
        rels = new_fields["relatives"]

        rels_add = set(rels) - set(prev_rels)
        rels_rem = set(prev_rels) - set(rels)

        for rel_id in rels_add.union(rels_rem):
            try:
                ctzns_for_upd[str(rel_id)] = ctzns[str(rel_id)]
            except KeyError as ve:
                abort(400, 'relative {} doesn\'t exist'.format(str(ve)))

        for rel_id in rels_add:
            ctzns_for_upd[str(rel_id)]["relatives"].append(ctzn_id)

        for rel_id in rels_rem:
            ctzns_for_upd[str(rel_id)]["relatives"].remove(ctzn_id)

    ctzn.update(new_fields)
    ctzns_for_upd[str(ctzn_id)] = ctzn

    db.imports.update_one(
        {"_id": imp_id},
        {'$set': ctzns_for_upd})

    return jsonify({"data": ctzn}), 200


@bp.route('/imports/<int:imp_id>/citizens', methods=['GET'])
def get_ctzns(imp_id: int):
    """Возвращает список всех жителей для указанного набора данных.

    """
    db = get_db()
    ctzns = db.imports.find_one({"_id": imp_id})

    if ctzns is None:
        abort(404, 'import doesn\'t exist')

    ctzns.pop("_id")

    ctzns = list(ctzns.values())

    return jsonify({"data": ctzns}), 200


@bp.route('/imports/<int:imp_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(imp_id: int):
    """Возвращает жителей и количество подарков, которые они будут покупать
    своим ближайшим родственникам (1-го порядка), сгруппированных по месяцам
    из указанного набора данных.

    Поиск перебором в цикле.
    """
    db = get_db()
    ctzns = db.imports.find_one({"_id": imp_id})

    if ctzns is None:
        abort(404, 'import doesn\'t exist')

    ctzns.pop("_id")
    months = dict((str(i), {}) for i in range(1, 13))

    for ctzn_id, ctzn in ctzns.items():
        for rel_id in ctzn["relatives"]:
            rel = ctzns[str(rel_id)]
            month = rel["birth_date"].split('.')[1].lstrip("0")

            try:
                c = months[month][int(ctzn_id)]
                c["presents"] += 1
            except KeyError:
                months[month][int(ctzn_id)] = {
                    "citizen_id": int(ctzn_id), "presents": 1
                }

    outs = dict((str(i), []) for i in range(1, 13))

    i = 1
    for month in months.values():
        outs[str(i)] = list(month.values())
        i += 1

    return jsonify({"data": outs}), 200


@bp.route('/imports/<int:imp_id>/towns/stat/percentile/age', methods=['GET'])
def get_age_stat(imp_id: int):
    """Возвращает статистику по городам для указанного набора данных в разрезе
    возраста (полных лет) жителей: p50, p75, p99, где число - это значение
    перцентиля.

    Для даты удаляются ведущие и завершающие пробелы.

    Колличество полных лет расчитывается по формуле:
    age = today.year - birth_date.year - int(
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    Условие в скобках либо вычитает год, если дня рождения ещё не было,
    либо не делает ничего, если день рождения уже был.
    """
    db = get_db()

    ctzns = db.imports.find_one({"_id": imp_id})

    if ctzns is None:
        abort(404, 'import doesn\'t exist')

    ctzns.pop("_id")
    towns = {}

    for ctzn in ctzns.values():
        birth_date = datetime.strptime(ctzn["birth_date"].strip(), "%d.%m.%Y")
        today = date.today()
        age = today.year - birth_date.year - int(
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )

        try:
            towns[ctzn["town"]].append(age)
        except KeyError:
            towns[ctzn["town"]] = [age]

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


@bp.errorhandler(400)
def bad_request(ex):

    return jsonify(error="Bad Request", description=ex.description), ex.code
