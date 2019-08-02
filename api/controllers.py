# -*- coding: utf-8 -*-
'''
Структура базы данных:
imports/import_id
{
    "_id": 1,
    "1": {"town": ...},
    "2": {"town": ...},
    ...
}
'''

from datetime import datetime, date

from flask import Blueprint, request, jsonify, abort
from jsonschema import validate, ValidationError
from numpy import percentile

from api.schemas import ctzn_schema, imp_schema
from api.db import get_db


bp = Blueprint('controllers', __name__)


@bp.route('/imports', methods=['POST'])
def post_imp():
    imp = request.get_json()
    try:
        validate(instance=imp, schema=imp_schema)

        ctzns = {}
        for ctzn in imp["citizens"]:
            ctzn_id = ctzn.pop("citizen_id")

            if ctzn_id in ctzns.keys():
                raise ValidationError('Уникальный идентификатор жителя')

            # mongodb требует ключи str
            ctzns[str(ctzn_id)] = ctzn

        for ctzn_id, ctzn in ctzns.items():
            for rel_id in ctzn["relatives"]:
                rel = ctzns[str(rel_id)]

                if int(ctzn_id) not in rel["relatives"]:
                    raise ValidationError("Родственные связи двусторонние")

    except ValidationError:
        abort(400)

    db = get_db()
    imp_id = db.imports.count_documents({}) + 1
    ctzns["_id"] = imp_id
    db.imports.insert_one(ctzns)

    return jsonify({"data": {"import_id": imp_id}}), 201


@bp.route('/imports/<int:imp_id>/citizens/<int:ctzn_id>',
          methods=['PATCH'])
def patch_ctzn(imp_id: int, ctzn_id: int):
    new_fields = request.get_json()
    try:
        validate(instance=new_fields, schema=ctzn_schema)

    except ValidationError:
        abort(400)

    db = get_db()
    ctzns = db.imports.find_one({"_id": imp_id})
    ctzn = ctzns[str(ctzn_id)]

    if "relatives" in new_fields:
        rels = new_fields["relatives"]

        for rel_id in rels:
            ctzns[str(rel_id)]["relatives"].append(ctzn_id)

    ctzn.update(new_fields)

    db.imports.update_one(
        {"_id": imp_id},
        {'$set': ctzns})

    ctzn["citizen_id"] = ctzn_id

    return jsonify({"data": ctzn}), 200


@bp.route('/imports/<int:imp_id>/citizens', methods=['GET'])
def get_ctzns(imp_id: int):
    db = get_db()
    ctzns = db.imports.find_one({"_id": imp_id})

    ctzns.pop("_id")
    for ctzn_id, ctzn in ctzns.items():
        ctzn["citizen_id"] = int(ctzn_id)
    ctzns = list(ctzns.values())

    return jsonify({"data": ctzns}), 200


@bp.route('/imports/<int:imp_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(imp_id: int):
    db = get_db()
    ctzns = db.imports.find_one({"_id": imp_id})
    if ctzns is None:
        abort(404)
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
    db = get_db()

    ctzns = db.imports.find_one({"_id": imp_id})
    ctzns.pop("_id")
    if ctzns is None:
        abort(404)

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
        stat["p50"] = percentile(towns[town], 50, interpolation='linear')
        stat["p75"] = percentile(towns[town], 75, interpolation='linear')
        stat["p99"] = percentile(towns[town], 99, interpolation='linear')
        stats.append(stat)

    return jsonify({"data": stats}), 200


@bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request"}), 400


@bp.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error"}), 500
