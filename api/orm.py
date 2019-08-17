# -*- coding: utf-8 -*-

import json
from datetime import date

import fastjsonschema
from fastjsonschema import JsonSchemaException, validate

"""
collection [
    {"import_id", "citizen_id", ...}
]
"""


class NotFound(Exception):
    pass


class Ctzn():
    def __init__(self, citizen_id, town, street, building, apartment, name,
                 birth_date, gender, relatives):
        self.citizen_id = citizen_id
        self.town = town
        self.street = street
        self.building = building
        self.apartment = apartment
        self.name = name
        self.birth_date = birth_date
        self.gender = gender
        self.relatives = relatives
        self.v = Validation()


class Validation():
    def __init__(self):
        self.for_imp = self.compile(json.load(open('api/schemas/imp.json')))
        self.for_crt = self.compile(json.load(open('api/schemas/crt_ctzn.json')))
        self.for_upd = self.compile(json.load(open('api/schemas/upd_ctzn.json')))

    def compile(self, schema):
        ref_handler = {"": lambda file: json.load(open('api/schemas/' + file))}
        validator = fastjsonschema.compile(schema, handlers=ref_handler)

        return validator

    def date(self, d):
        dd, mm, yyyy = map(int, d.split('.'))
        try:
            date(yyyy, mm, dd)
        except ValueError as ve:
            raise JsonSchemaException(ve)


class CtznsDAO():
    def __init__(self, mongo_db):
        self.mongo_db = mongo_db
        self.collection.create_index("import_id")
        self.collection.create_index("citizen_id")
        self.v = Validation()

    @property
    def collection(self):
        return self.mongo_db['citizens']

    def create(self, imp):
        self.v.for_imp(imp)
        ctzns = {}
        imp_id = self.collection.count_documents({}) + 1

        for ctzn in imp["citizens"]:
            self.v.for_crt(ctzn)
            self.v.date(ctzn["birth_date"])
            ctzn_id = ctzn["citizen_id"]

            if str(ctzn_id) in ctzns.keys():
                raise JsonSchemaException('citizen_ids are not unique')

            ctzn["import_id"] = imp_id
            ctzns[str(ctzn_id)] = ctzn

        for ctzn_id, ctzn in ctzns.items():
            for rel_id in ctzn["relatives"]:
                rel = ctzns[str(rel_id)]

                if int(ctzn_id) not in rel["relatives"]:
                    raise JsonSchemaException(
                        "citizens relatives are not bidirectional"
                    )

        self.collection.insert_many(ctzns.values())

        return imp_id

    def read(self, imp_id):
        ctzns = self.collection.find({"import_id": imp_id}, {"_id": 0})
        if not ctzns:
            raise NotFound('import doesn\'t exist')
        d = {}

        for ctzn in ctzns:
            ctzn.pop("import_id")
            d[str(ctzn["citizen_id"])] = ctzn
        return d

    def update(self, imp_id, ctzn_id, flds):
        ctzns = self.read(imp_id)
        # if not str(ctzn_id) in ctzns:
        #    raise NotFound('citizen doesn\'t exist')

        self.v.for_upd(flds)
        ctzns_for_upd = {}
        if "birth_date" in flds:
            self.v.date(flds["birth_date"])

        ctzn = ctzns[str(ctzn_id)]

        if "relatives" in flds:
            rels = flds["relatives"]
            prev_rels = ctzn["relatives"]

            rels_add = set(rels) - set(prev_rels)
            rels_rem = set(prev_rels) - set(rels)

            for rel_id in rels_add.union(rels_rem):
                try:
                    ctzns_for_upd[str(rel_id)] = ctzns[str(rel_id)]
                except KeyError as ve:
                    raise JsonSchemaException('relative {} doesn\'t exist'.format(str(ve)))

            for rel_id in rels_add:
                ctzns_for_upd[str(rel_id)]["relatives"].append(ctzn_id)

            for rel_id in rels_rem:
                ctzns_for_upd[str(rel_id)]["relatives"].remove(ctzn_id)

        ctzn.update(flds)
        ctzns_for_upd[str(ctzn_id)] = ctzn
        self.collection.update_one(
            {"_id": imp_id},
            {'$set': ctzns_for_upd}
        )
        return ctzn

    def delete(self, ctzn):
        pass
