# -*- coding: utf-8 -*-
'''
Структура базы данных:
imports/import_id
{
    "_id": 1,
    "1": {"citizen_id": 1, "town": ...},
    "2": {"citizen_id": 2, "town": ...},
    ...
}
'''

import sys
from datetime import datetime, date

from flask import Blueprint, request, jsonify, abort
import json
import fastjsonschema
from fastjsonschema import JsonSchemaException
from numpy import percentile

from api.db import get_db


bp = Blueprint('controllers', __name__)


@bp.route('/imports', methods=['POST'])
def post_imp():
    imp = request.get_json()
    try:
        schema = json.load(open('api/schemas/imp.json'))
        fastjsonschema.validate(schema, imp)

        ctzns = {}
        schema = json.load(open('api/schemas/crt_ctzn.json'))
        validator = fastjsonschema.compile(schema)

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
        sys.stderr.write(str(ve))
        abort(400, str(ve))

    db = get_db()
    imp_id = db.imports.count_documents({}) + 1
    ctzns["_id"] = imp_id
    db.imports.insert_one(ctzns)

    return jsonify({"data": {"import_id": imp_id}}), 201


@bp.route('/imports/<int:imp_id>/citizens/<int:ctzn_id>',
          methods=['PATCH'])
def patch_ctzn(imp_id: int, ctzn_id: int):
    new_fields = request.get_json()
    schema = json.load(open('api/schemas/upd_ctzn.json'))
    try:
        fastjsonschema.validate(schema, new_fields)

    except JsonSchemaException as ve:
        sys.stderr.write(str(ve))
        abort(400, str(ve))

    db = get_db()
    ctzns = db.imports.find_one({"_id": imp_id})
    ctzns_for_upd = {}

    if ctzns is None or not str(ctzn_id) in ctzns:
        abort(404)

    ctzn = ctzns[str(ctzn_id)]

    if "relatives" in new_fields:
        prev_rels = ctzn["relatives"]
        rels = new_fields["relatives"]

        rels_add = set(rels) - set(prev_rels)
        rels_rem = set(prev_rels) - set(rels)

        for rel_id in rels_add.union(rels_rem):
            ctzns_for_upd[str(rel_id)] = ctzns[str(rel_id)]

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
    db = get_db()
    ctzns = db.imports.find_one({"_id": imp_id})

    if ctzns is None:
        abort(404)

    ctzns.pop("_id")

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
    response = jsonify(
        {"error": "Bad Request", "description": error.description})
    return response, 400


@bp.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error"}), 500
