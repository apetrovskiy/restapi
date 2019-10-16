# -*- coding: utf-8 -*-
"""
    REST API
    ~~~~~~~~

    Структура
    ~~~~~~~~~

    .. api.db
        Подключение базы данных

    .. api.orm
        Обертка для pymongo

    .. api.controllers
        Реализация обработчиков

    .. schemas
        Схемы для валидации данных в обработчиках

    Конфигурирование
    ~~~~~~~~~~~~~~~~

    Конфигурирование доступно через переменные окружения

    .. MONGO_URI
        uri для подключения к mongodb

    .. MONGO_DBNAME
        Имя основной базы данных

    .. LOG_FILE
        Путь к файлу логов

    Функции
    ~~~~~~~

    .. create_app(config: dict=None)
        Инициализирует поток приложения

"""

import os
import logging
import traceback

from flask import Flask, jsonify

__all__ = ["create_app"]


def create_app(config: dict = None):
    app = Flask(__name__)

    if config:
        app.config.from_mapping(config)
    else:
        app.config.from_mapping(
            MONGO_URI=os.environ['MONGO_URI'],
            MONGO_DBNAME=os.environ['MONGO_DBNAME'],
            LOG_FILE=os.environ['LOG_FILE']
        )

    file_handler = logging.FileHandler(app.config['LOG_FILE'])
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s:\n%(message)s"
    )
    file_handler.setFormatter(formatter)

    app.logger.addHandler(file_handler)

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(405)
    def _handle_api_error(ex):
        nms = {
            400: "Bad Request",
            404: "Not Found",
            405: "Method Not Allowed"
        }

        return jsonify(error=nms[ex.code], description=ex.description), ex.code

    @app.errorhandler(Exception)
    def _handle_unexpected_error(ex):
        app.logger.error(traceback.format_exc())

        return jsonify(error="Internal Server Error"), 500

    from . import db
    db.init_app(app)

    from . import controllers
    app.register_blueprint(controllers.bp)

    return app
