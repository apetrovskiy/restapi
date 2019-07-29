# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, abort, current_app
from jsonschema import validate, ValidationError

from api.schemas import *
from api.db import get_db


bp = Blueprint('controllers', __name__)


@bp.route('/imports', methods=['POST'])
def post_import():
    db = get_db()
    import_ = request.get_json()
    try:
        validate(instance=import_, schema=citizens_schema)
        c_ids = []
        for citizen in import_["citizens"]:
            validate_unique_citizen_id(citizen, c_ids)
            validate_relatives(citizen, import_["citizens"])
    except ValidationError:
        abort(400)
    import_id = db.imports.count_documents({}) + 1
    import_["data"] = {"import_id": import_id}
    db.imports.insert_one(import_)
    return jsonify({"data": import_["data"]}), 201


@bp.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_citizens(import_id):
    db = get_db()
    data = db.imports.find_one({"data.import_id": import_id})
    if not data:
        abort(404)
    return jsonify({"data": data["citizens"]}), 200


@bp.route('/imports/<int:import_id>/citizens/<int:citizen_id>',
          methods=['PATCH'])
def patch_citizen(import_id, citizen_id):
    db = get_db()
    data = db.imports.find_one({"data.import_id": import_id})
    if not data:
        abort(404)

    for citizen in data["citizens"]:
        if citizen["citizen_id"] == citizen_id:
            new_data = request.get_json()
            # валидация новых данных
            citizen.update(new_data)
            break
    else:
        abort(404)

    db.imports.update_one(
        {"data": {"import_id": import_id}},
        {'$set': {"citizens": data["citizens"]}})

    return jsonify({"data": citizen}), 200


@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request'}), 400


@bp.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500
