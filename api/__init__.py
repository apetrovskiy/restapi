# -*- coding: utf-8 -*-

import os

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        MONGO_URI=os.environ.get("MONGO_URI", "mongodb://localhost:27017/"),
        MONGO_DB_NAME=os.environ.get("MONGO_DB_NAME", "dev5")
    )

    from . import db
    db.init_app(app)

    from . import controllers
    app.register_blueprint(controllers.bp)

    return app
