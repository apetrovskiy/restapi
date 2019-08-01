# -*- coding: utf-8 -*-

from datetime import datetime, date

from flask import Blueprint, request, jsonify, abort
from jsonschema import validate, ValidationError
from numpy import percentile

from api.schemas import ctzn_schema, imp_schema
from api.db import get_db


bp = Blueprint('controllers', __name__)


@bp.route('/imports', methods=['POST'])
def post_imp():
    db = get_db()
    imp = request.get_json()

    try:
        validate(instance=imp, schema=imp_schema)

        ctzns = {}
        for ctzn in imp["citizens"]:
            # citizen_id храниться и как ключ, и как значение
            # запрет на изменение в других местах
            ctzn_id = ctzn["citizen_id"]
            if ctzn_id in ctzns.keys():
                raise ValidationError("Уникальный идентификатор жителя")
            ctzns[str(ctzn_id)] = ctzn

        for ctzn in ctzns.values():
            for rel_id in ctzn["relatives"]:
                rel = ctzns[str(rel_id)]
                if ctzn["citizen_id"] not in rel["relatives"]:
                    raise ValidationError("Родственные связи двусторонние")

    except ValidationError:
        abort(400)

    doc = {}
    imp_id = db.imports.count_documents({}) + 1
    doc["data"] = {"import_id": imp_id}
    doc["citizens"] = ctzns
    db.imports.insert_one(doc)

    return jsonify({"data": doc["data"]}), 201


@bp.route('/imports/<int:imp_id>/citizens/<int:ctzn_id>',
          methods=['PATCH'])
def patch_ctzn(imp_id: int, ctzn_id: int):
    db = get_db()
    try:
        ctzns = db.imports.find_one(
            {"data.import_id": imp_id}
        )["citizens"]
    except TypeError:
        abort(404)

    ctzn = ctzns[str(ctzn_id)]
    new_fields = request.get_json()

    try:
        validate(instance=new_fields, schema=ctzn_schema)

    except ValidationError:
        abort(400)

    if new_fields["relatives"]:
        rels = new_fields["relatives"]

        for rel_id in rels:
            ctzns[str(rel_id)]["relatives"].append(ctzn_id)

    ctzn.update(new_fields)

    db.imports.update_one(
        {"data": {"import_id": imp_id}},
        {'$set': {"citizens": ctzns}})

    return jsonify({"data": ctzn}), 200


@bp.route('/imports/<int:imp_id>/citizens', methods=['GET'])
def get_ctzns(imp_id: int):
    db = get_db()
    try:
        ctzns = db.imports.find_one({"data.import_id": imp_id})["citizens"]
    except TypeError:
        abort(404)

    ctzns = list(ctzns.values())

    return jsonify({"data": ctzns}), 200


@bp.route('/imports/<int:imp_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(imp_id: int):
    db = get_db()
    try:
        ctzns = db.imports.find_one({"data.import_id": imp_id})["citizens"]
    except TypeError:
        abort(404)

    months = dict((str(i), {}) for i in range(1, 13))

    for ctzn in ctzns.values():
        for rel_id in ctzn["relatives"]:
            rel = ctzns[str(rel_id)]
            month = rel["birth_date"].split('.')[1].lstrip("0")
            ctzn_id = ctzn["citizen_id"]

            try:
                c = months[month][ctzn_id]
                c["presents"] += 1
            except KeyError:
                months[month][ctzn_id] = {
                    "citizen_id": ctzn["citizen_id"], "presents": 1
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
    try:
        ctzns = db.imports.find_one({"data.import_id": imp_id})["citizens"]
    except TypeError:
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
