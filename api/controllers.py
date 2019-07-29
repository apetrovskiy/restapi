# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, abort, current_app
from jsonschema import validate, ValidationError

from api.schemas import (
    ctzn_schema, imp_schema, get_ctzn, validate_relatives, validate_unique_id)
from api.db import get_db


bp = Blueprint('controllers', __name__)


@bp.route('/imports', methods=['POST'])
def post_imp():
    db = get_db()
    imp = request.get_json()

    try:
        validate(instance=imp, schema=imp_schema)

        c_ids = set()  # Использованные citizen_id
        for ctzn in imp["citizens"]:
            validate_unique_id(ctzn["citizen_id"], c_ids)
            validate_relatives(ctzn, imp["citizens"])

    except ValidationError:
        abort(400)

    imp_id = db.imports.count_documents({}) + 1
    imp["data"] = {"import_id": imp_id}
    db.imports.insert_one(imp)

    return jsonify({"data": imp["data"]}), 201


@bp.route('/imports/<int:imp_id>/citizens/<int:ctzn_id>',
          methods=['PATCH'])
def patch_ctzn(imp_id: int, ctzn_id: int):
    db = get_db()
    try:
        ctzns = db.imports.find_one({"data.import_id": imp_id})["citizens"]
    except TypeError:
        abort(404)

    ctzn = get_ctzn(ctzn_id, ctzns)
    if ctzn is None:
        abort(404)

    new_fields = request.get_json()

    try:
        validate(instance=new_fields, schema=ctzn_schema)

    except ValidationError:
        abort(400)

    try:
        rels = new_fields["relatives"]

        for rel_id in rels:
            rel = get_ctzn(rel_id, ctzns)
            rel["relatives"].append(ctzn_id)

    except KeyError:
        pass

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

    return jsonify({"data": ctzns}), 200


@bp.route('/imports/<int:imp_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(imp_id):
    db = get_db()
    try:
        ctzns = db.imports.find_one({"data.import_id": imp_id})["citizens"]
    except TypeError:
        abort(404)

    months = dict((str(i), []) for i in range(1, 13))

    for ctzn in ctzns:
        for rel_id in ctzn["relatives"]:
            rel = get_ctzn(rel_id, ctzns)
            month = rel["birth_date"].split('.')[1].lstrip("0")

            try:
                c = get_ctzn(ctzn["citizen_id"], months[month])
                c["presents"] += 1
            except TypeError:
                months[month].append(
                    {"citizen_id": ctzn["citizen_id"], "presents": 1})

    return jsonify({"data": months}), 200


@bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request"}), 400


@bp.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error"}), 500
