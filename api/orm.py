# -*- coding: utf-8 -*-
"""
    Методы
    ~~~~~~

    .. CtznDAO.create(import_data)

    .. CtznDAO.read(import_id)

    .. CtznDAO.update(import_id, citizen_id, fields_for_update)

    .. CtznDAO.delete(import_id)

"""

import random
from typing import Dict, Any, List

from pymongo.collection import Collection

from api.db import get_db
from api.validation import (
    validate_import_citizens, validate_patch_citizen, NotFound)

__all__ = ["CtznsDAO"]


class CtznsDAO:
    """Реализует методы для создания, чтения, редактирования и удаления
    наборов с данными о жителях.

    """

    @property
    def collection(self) -> Collection:
        return get_db()['imports']

    def _create_id(self) -> int:
        _id = random.randint(0, 10 ** 9)

        while self.collection.find_one({"_id": _id}) is not None:
            _id = random.randint(0, 10 ** 9)

        return _id

    def create(self, imp: Dict[str, List[Dict[str, Any]]]) -> int:
        """Проверяет и создает набор с данными о жителях."""

        imp_id = self._create_id()
        ctzns_and_id: Dict[str, Any] = validate_import_citizens(imp)
        ctzns_and_id["_id"] = imp_id
        self.collection.insert_one(ctzns_and_id)

        return imp_id

    def read(self, imp_id: int) -> Dict[str, Dict[str, Any]]:
        """Возвращает набор с данными о жителях."""

        ctzns: Dict[str, Dict[str, Any]] = self.collection.find_one(
            {"_id": imp_id}, {"_id": 0})
        if ctzns is None:
            raise NotFound('import doesn\'t exist')

        return ctzns

    def update(
            self,
            imp_id: int,
            ctzn_id: int,
            flds: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновляет данные о жителе в наборе."""

        ctzns = self.read(imp_id)
        ctzns_for_upd = validate_patch_citizen(ctzns, ctzn_id, flds)

        self.collection.update_one(
            {"_id": imp_id},
            {'$set': ctzns_for_upd}
        )

        return ctzns_for_upd[str(ctzn_id)]

    def delete(self, imp_id: int) -> None:
        """Удаляет набор с данными о жителях."""

        n = self.collection.delete_one({"_id": imp_id}).raw_result["n"]
        if n == 0:
            raise NotFound('import doesn\'t exist')
