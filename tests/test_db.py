# -*- coding: utf-8 -*-


def test_drop_db_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_drop_db():
        Recorder.called = True

    monkeypatch.setattr('api.mongo_orm.drop_db', fake_drop_db)
    result = runner.invoke(args=['drop-db'])
    assert 'is dropped' in result.output
    assert Recorder.called
