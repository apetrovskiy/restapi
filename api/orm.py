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
from typing import Callable, Dict, Any, List

import fastjsonschema
from pymongo.collection import Collection

from api.db import get_db

__all__ = ["NotFound", "ValidationError", "CtznsDAO"]


class NotFound(Exception):
    """При вызове методов для несуществующих import_id или citizen_id"""

    pass


class ValidationError(Exception):
    """При ошибках валидации"""

    pass


class _Validation:
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

    @staticmethod
    def compile(schema: dict) -> Callable[..., None]:
        ref_handler = {"": lambda file: json.load(open(f'api/schemas/{file}'))}
        validator = fastjsonschema.compile(schema, handlers=ref_handler)

        return validator

    @staticmethod
    def date(d: str) -> None:
        if d is None:
            return

        dd, mm, yyyy = map(int, d.split('.'))
        try:
            check = date(yyyy, mm, dd)
        except ValueError as ve:
            raise ValidationError(ve)

        today = date.today()

        if check >= today:
            raise ValidationError(
                'birth date must be less than the current date'
            )

    @staticmethod
    def contain_ln(s: str) -> None:
        if s is None:
            return

        contain = any(
            c.isalpha() or c.isdigit()
            for c in s
        )
        if not contain:
            raise ValidationError('data must contain letter or number')


class CtznsDAO:
    """Реализует методы для создания, чтения, редактирования и удаления
    наборов с данными о жителях.

    """
    def __init__(self):
        self.v = _Validation()

    @property
    def collection(self) -> Collection:
        return get_db()['imports']

    def _create_id(self, start: int = 1) -> int:
        _id = start

        while self.collection.find_one({"_id": _id}) is not None:
            _id += 1

        return _id

    def create(self, imp: Dict[str, List[Dict[str, Any]]]) -> int:
        """Проверяет и создает набор с данными о жителях."""

        try:
            self.v.for_imp(imp)

        except fastjsonschema.JsonSchemaException as ve:
            raise ValidationError(ve)

        ctzns: Dict[str, Dict[str, Any]] = {}

        for ctzn in imp["citizens"]:
            try:
                self.v.for_crt(ctzn)

            except fastjsonschema.JsonSchemaException as ve:
                raise ValidationError(ve)

            self.v.contain_ln(ctzn["town"])
            self.v.contain_ln(ctzn["street"])
            self.v.contain_ln(ctzn["building"])

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
        ctzns_and_id: Dict[str, Any] = ctzns
        ctzns_and_id["_id"] = imp_id
        self.collection.insert_one(ctzns_and_id)

        return imp_id

    def read(self, imp_id: int) -> Dict[str, Dict[str, Any]]:
        """Возвращает набор с данными о жителях."""

        ctzns = self.collection.find_one({"_id": imp_id}, {"_id": 0})
        if ctzns is None:
            raise NotFound('import doesn\'t exist')

        return ctzns

    @staticmethod
    def _update_relatives(
            rels: List[int],
            prev_rels: List[int],
            ctzns: Dict[str, Dict[str, Any]],
            ctzn_id: int
    ) -> Dict[str, dict]:
        if rels is None or prev_rels is None:
            return {}

        rels_add = set(rels) - set(prev_rels)
        rels_rem = set(prev_rels) - set(rels)

        ctzns_for_upd = {}
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

        return ctzns_for_upd

    def update(
            self,
            imp_id: int,
            ctzn_id: int,
            flds: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновляет данные о жителе в наборе."""

        ctzns = self.read(imp_id)
        if not str(ctzn_id) in ctzns:
            raise NotFound('citizen doesn\'t exist')
        ctzn = ctzns[str(ctzn_id)]
        try:
            self.v.for_upd(flds)

        except fastjsonschema.JsonSchemaException as ve:
            raise ValidationError(ve)

        for field in ("street", "town", "building"):
            self.v.contain_ln(flds.get(field, None))

        self.v.date(flds.get("birth_date", None))

        ctzns_for_upd = self._update_relatives(
            flds.get("relatives", None),
            ctzn.get("relatives", None),
            ctzns,
            ctzn_id
        )

        ctzn.update(flds)
        ctzns_for_upd[str(ctzn_id)] = ctzn
        self.collection.update_one(
            {"_id": imp_id},
            {'$set': ctzns_for_upd}
        )

        return ctzn

    def delete(self, imp_id: int) -> None:
        """Удаляет набор с данными о жителях."""

        n = self.collection.delete_one({"_id": imp_id}).raw_result["n"]
        if n == 0:
            raise NotFound('import doesn\'t exist')
