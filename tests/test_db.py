# -*- coding: utf-8 -*-

from api.db import get_db


def test_get_db(app):
    with app.app_context():
        db = get_db()
        assert db == get_db()


def test_drop_db_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_drop_db():
        Recorder.called = True

    monkeypatch.setattr('api.db.drop_db', fake_drop_db)
    result = runner.invoke(args=['drop-db'])
    assert 'is dropped' in result.output
    assert Recorder.called
