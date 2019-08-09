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


    Функции
    ~~~~~~~

    .. create_app()
        Инициализирует поток приложения
"""
import os

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        MONGO_URI=os.environ.get("MONGO_URI", "mongodb://localhost:27017/"),
        MONGO_DB_NAME=os.environ.get("MONGO_DB_NAME", "dev")
    )

    from . import db
    db.init_app(app)

    from . import controllers
    app.register_blueprint(controllers.bp)

    return app
