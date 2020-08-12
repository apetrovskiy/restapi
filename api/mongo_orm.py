import ujson
from bson import ObjectId
from fastapi import HTTPException
from pymongo import MongoClient, UpdateOne
from pymongo.database import Database

from api.schema import (Citizens, Import, ObjectIdStr, PrettyCitizens,
                        from_pretty)

from . import config


def get_db() -> Database:
    """
    Возвращает текущую базу данных.
    """
    client = MongoClient(config.settings.mongo_uri)

    return client[config.settings.mongo_dbname]


def create(import_: Import) -> ObjectId:
    """
    Сохраняет набор с данными о жителях.
    """
    result = get_db().imports.insert_one(ujson.loads(import_.json()))
    # Collection.insert_one() принимает на вход json, а Model.json()
    # возвращает строку сериализованную с помощью custom json encoders.

    return result.inserted_id


def read(import_id: ObjectIdStr) -> Citizens:
    """
    Возвращает список всех жителей для указанного набора данных.
    """
    record = get_db().imports.find_one({"_id": import_id}, {"_id": 0})

    if record is None:
        raise HTTPException(status_code=404, detail="Import not found")

    return Citizens(**record)


def update(import_id: ObjectIdStr, different_citizens: PrettyCitizens):
    """
    Изменяет информацию о жителях в указанном наборе данных.
    """
    record = Citizens(citizens=from_pretty(different_citizens))
    operations = [
        UpdateOne({
            "_id": import_id,
            "citizens.citizen_id": citizen.citizen_id
        }, {
            "$set": {
                "citizens.$": ujson.loads(citizen.json())
            }
        }) for citizen in record.citizens
    ]
    # UpdateOne.$set принимает на вход json, а Model.json() возвращает строку
    # сериализованную с помощью custom json encoders.

    get_db().imports.bulk_write(operations, ordered=False)
