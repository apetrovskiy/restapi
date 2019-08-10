# -*- coding: utf-8 -*-
"""
    REST API
    ~~~~~~~~

    Структура
    ~~~~~~~~~

    .. api.db
        Обертка для pymongo

    .. api.controllers
        Реализация обработчиков

    .. schemas
        Схемы для валидации данных в обработчиках


    Переменные окружения
    ~~~~~~~~~~~~~~~~~~~~

    .. MONGO_URI
        uri для подключения к mongodb

    .. MONGO_DB_NAME
        Имя основной базы данных (Для тестовой используется test)

    .. LOGS_DIR
        Путь к папке с логами ошибок

    Функции
    ~~~~~~~

    .. create_app()
        Инициализирует поток приложения
"""

import os
import os.path
import logging
import traceback

from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        MONGO_URI=os.environ.get("MONGO_URI", "mongodb://localhost:27017/"),
        MONGO_DB_NAME=os.environ.get("MONGO_DB_NAME", "dev"),
        LOGS_DIR=os.environ.get("LOGS_DIR", "logs/")
    )

    if not os.path.exists(app.config['LOGS_DIR']):
        os.makedirs(app.config['LOGS_DIR'])

    file_handler = logging.FileHandler(app.config['LOGS_DIR'] + 'api.log')
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s:\n%(message)s"
    )
    file_handler.setFormatter(formatter)

    app.logger.addHandler(file_handler)

    @app.errorhandler(404)
    @app.errorhandler(405)
    def _handle_api_error(ex):
        nms = {
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
