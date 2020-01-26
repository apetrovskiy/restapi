# -*- coding: utf-8 -*-
"""
    REST API
    ~~~~~~~~

    Структура
    ~~~~~~~~~

    .. api.db
        Подключение базы данных

    .. api.validation
        Валидация данных

    .. api.orm
        Обертка для pymongo

    .. api.controllers
        Реализация обработчиков

    .. citizen_schema.py
        Схема для валидации данных в обработчиках

    Конфигурирование
    ~~~~~~~~~~~~~~~~

    Конфигурирование доступно через переменные окружения

    .. MONGO_URI
        uri для подключения к mongodb

    .. MONGO_DBNAME
        Имя основной базы данных

    Функции
    ~~~~~~~

    .. create_app(config: Optional[dict] = None) -> Flask
        Инициализирует поток приложения

"""

import os
import traceback

from flask import Flask, jsonify, make_response
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

    from . import db
    db.init_app(app)

    from . import controllers
    app.register_blueprint(controllers.bp, url_prefix='/imports')

    return app
