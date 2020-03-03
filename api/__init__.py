# -*- coding: utf-8 -*-
"""
    REST API
    ~~~~~~~~

    Структура
    ~~~~~~~~~

    .. api.citizen_schema
        Валидация данных и модели

    .. api.controllers
        Реализация обработчиков

    .. api.functions
        Функции для работы с данными

    .. api.mongo_orm
        Обертка для pymongo и CRUD

    Конфигурирование
    ~~~~~~~~~~~~~~~~

    Конфигурирование доступно через переменные окружения

    .. MONGO_URI
        uri для подключения к mongodb

    .. MONGO_DBNAME
        Имя основной базы данных

    .. MONGO_TESTDBNAME
        Имя базы данных, создающаейся во время тестов

    Функции
    ~~~~~~~

    .. create_app(config: Optional[Dict[str, str] = None) -> Flask
        Инициализирует поток приложения

"""

import os
import traceback

from flask import Flask, jsonify, make_response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from typing import Optional, Dict, Any

__all__ = ["create_app"]


def create_app(config: Optional[Dict[str, str]] = None) -> Flask:
    app = Flask(__name__)

    if config:
        app.config.from_mapping(config)
    else:
        app.config.from_mapping(
            MONGO_URI=os.environ['MONGO_URI'],
            MONGO_DBNAME=os.environ['MONGO_DBNAME']
        )

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(405)
    def _handle_api_error(ex: HTTPException) -> Any:
        return make_response(
            jsonify(
                error=ex.code,
                description=ex.description
            ),
            ex.code
        )

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def _handle_unexpected_error(exc: Exception) -> Any:
        app.logger.error(traceback.format_exc())
        return make_response(
            jsonify(
                error=500,
                description="Internal Server Error"
            ),
            500
        )

    from . import mongo_orm
    mongo_orm.init_app(app)

    from . import controllers
    app.register_blueprint(controllers.bp, url_prefix='/imports')

    CORS(app, resources={
        r"/imports*": {
            "origins": "*"
        }
    })

    return app
