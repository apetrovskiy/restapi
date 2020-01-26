# -*- coding: utf-8 -*-
"""
    Исключения
    ~~~~~~~~~~

    .. NotFound

    Функции
    ~~~~~~~

    .. validate_import_citizens(imp: dict) -> dict
        Проверяет набор с данными о жителях.

    .. validate_patch_citizen(ctzns: dict, ctzn_id: int, flds: dict) -> dict
        Проверяет данные жителя

"""

from typing import Dict, Any, List

from marshmallow import RAISE
from marshmallow import ValidationError

from api.citizen_schema import Citizen

__all__ = ["NotFound", "ValidationError", "validate_import_citizens",
           "validate_patch_citizen"]


class NotFound(Exception):
    """При вызове методов для несуществующих import_id или citizen_id"""

    pass


def validate_import_citizens(
    imp: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Dict[str, Any]]:
    """Проверяет набор с данными о жителях."""

    if 'citizens' not in imp:
        raise ValidationError('Import must contain "citizens" field')

    validate = Citizen(unknown=RAISE).load
    ctzns: Dict[str, Dict[str, Any]] = {}
    ctzns_ids: List[int] = []
    relatives: Dict[int, List[int]] = {}
    for ctzn in imp["citizens"]:
        validate(ctzn)
        ctzn_id = ctzn["citizen_id"]
        ctzns[str(ctzn_id)] = ctzn
        ctzns_ids.append(ctzn_id)
        relatives[ctzn_id] = ctzn["relatives"]

    if len(set(ctzns_ids)) != len(ctzns_ids):
        raise ValidationError('citizen_ids are not unique')

    for ctzn_id, rel_ids in relatives.items():
        for rel_id in rel_ids:
            if ctzn_id not in ctzns[str(rel_id)]["relatives"]:
                raise ValidationError(
                    "citizens relatives are not bidirectional"
                )

    return ctzns


def update_relatives(
        rels: List[int],
        prev_rels: List[int],
        ctzns: Dict[str, Dict[str, Any]],
        ctzn_id: int
) -> Dict[str, Dict[str, Any]]:
    if rels is None or prev_rels is None:
        return {}

    rels_add = set(rels) - set(prev_rels)
    rels_rem = set(prev_rels) - set(rels)

    ctzns_for_upd: Dict[str, Dict[str, Any]] = {}
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


def validate_patch_citizen(
        ctzns: Dict[str, Dict[str, Any]],
        ctzn_id: int,
        flds: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """Проверяет данные жителя."""

    if not flds:
        raise ValidationError("Data must be not empty")

    if not str(ctzn_id) in ctzns:
        raise NotFound('citizen doesn\'t exist')
    ctzn = ctzns[str(ctzn_id)]
    Citizen(unknown=RAISE, partial=True).load(flds)

    ctzns_for_upd = update_relatives(
        flds.get("relatives", None),
        ctzn.get("relatives", None),
        ctzns,
        ctzn_id
    )

    ctzn.update(flds)
    ctzns_for_upd[str(ctzn_id)] = ctzn

    return ctzns_for_upd
