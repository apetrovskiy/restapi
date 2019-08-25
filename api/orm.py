# -*- coding: utf-8 -*-
"""
    Исключения
    ~~~~~~~~~~

    .. NotFound

    .. ValidationError

    Методы
    ~~~~~~

    .. CtznDAO.create(import_data)

    .. CtznDAO.read(import_id)

    .. CtznDAO.update(import_id, citizen_id, fields_for_update)

    .. CtznDAO.delete(import_id)

"""

import json
from datetime import date

import fastjsonschema

from api.db import get_db

__all__ = ["NotFound", "ValidationError", "CtznsDAO"]


class NotFound(Exception):
    """При вызове методов для несуществующих import_id или citizen_id"""

    pass


class ValidationError(Exception):
    """При ошибках валидации"""

    pass


class _Validation():
    """Реализует расширенные методы валидации."""

    def __init__(self):
        self.for_imp = self.compile(json.load(open(
            'api/schemas/imp.json'
        )))
        self.for_crt = self.compile(json.load(open(
            'api/schemas/crt_ctzn.json'
        )))
        self.for_upd = self.compile(json.load(open(
            'api/schemas/upd_ctzn.json'
        )))

    def compile(self, schema):
        ref_handler = {"": lambda file: json.load(open(f'api/schemas/{file}'))}
        validator = fastjsonschema.compile(schema, handlers=ref_handler)

        return validator

    def date(self, d):
        dd, mm, yyyy = map(int, d.split('.'))
        try:
            date(yyyy, mm, dd)
        except ValueError as ve:
            raise ValidationError(ve)


class CtznsDAO():
    """Реализует методы для создания, чтения, редактирования и удаления
    наборов с данными о жителях.

    """
    def __init__(self):
        self.v = _Validation()

    @property
    def collection(self):
        return get_db()['imports']

    def _create_id(self, start=1) -> int:
        id = start

        while self.collection.find_one({"_id": id}) is not None:
            id += 1

        return id

    def create(self, imp):
        """Проверяет и создает набор с данными о жителях."""

        try:
            self.v.for_imp(imp)

        except fastjsonschema.JsonSchemaException as ve:
            raise ValidationError(ve)

        ctzns = {}

        for ctzn in imp["citizens"]:
            try:
                self.v.for_crt(ctzn)

            except fastjsonschema.JsonSchemaException as ve:
                raise ValidationError(ve)

            self.v.date(ctzn["birth_date"])
            ctzn_id = ctzn["citizen_id"]
            if str(ctzn_id) in ctzns.keys():
                raise ValidationError('citizen_ids are not unique')
            ctzns[str(ctzn_id)] = ctzn

        for ctzn_id, ctzn in ctzns.items():
            for rel_id in ctzn["relatives"]:
                rel = ctzns[str(rel_id)]
                if int(ctzn_id) not in rel["relatives"]:
                    raise ValidationError(
                        "citizens relatives are not bidirectional"
                    )

        imp_id = self._create_id()
        ctzns["_id"] = imp_id
        self.collection.insert_one(ctzns)

        return imp_id

    def read(self, imp_id):
        """Возвращает набор с данными о жителях."""

        ctzns = self.collection.find_one({"_id": imp_id}, {"_id": 0})
        if ctzns is None:
            raise NotFound('import doesn\'t exist')

        return ctzns

    def update(self, imp_id, ctzn_id, flds):
        """Обновляет данные о жителе в наборе."""

        ctzns = self.read(imp_id)
        if not str(ctzn_id) in ctzns:
            raise NotFound('citizen doesn\'t exist')
        ctzn = ctzns[str(ctzn_id)]
        try:
            self.v.for_upd(flds)

        except fastjsonschema.JsonSchemaException as ve:
            raise ValidationError(ve)

        ctzns_for_upd = {}
        if "birth_date" in flds:
            self.v.date(flds["birth_date"])
        if "relatives" in flds:
            rels = flds["relatives"]
            prev_rels = ctzn["relatives"]

            rels_add = set(rels) - set(prev_rels)
            rels_rem = set(prev_rels) - set(rels)

            for rel_id in rels_add.union(rels_rem):
                try:
                    rel = ctzns[str(rel_id)]
                    ctzns_for_upd[str(rel_id)] = rel

                except KeyError as ve:
                    raise ValidationError(
                        f'relative {str(ve)} doesn\'t exist'
                    )

            for rel_id in rels_add:
                rel = ctzns_for_upd[str(rel_id)]
                rel["relatives"].append(ctzn_id)

            for rel_id in rels_rem:
                rel = ctzns_for_upd[str(rel_id)]
                rel["relatives"].remove(ctzn_id)

        ctzn.update(flds)
        ctzns_for_upd[str(ctzn_id)] = ctzn
        self.collection.update_one(
            {"_id": imp_id},
            {'$set': ctzns_for_upd}
        )

        return ctzn

    def delete(self, imp_id):
        """Удаляет набор с данными о жителях."""

        n = self.collection.delete_one({"_id": imp_id}).raw_result["n"]
        if n == 0:
            raise NotFound('import doesn\'t exist')
