# -*- coding: utf-8 -*-

from _pytest.monkeypatch import MonkeyPatch
from flask.testing import FlaskCliRunner


def test_drop_db_command(
        runner: FlaskCliRunner,
        monkeypatch: MonkeyPatch
) -> None:
    class Recorder:
        called = False

    def fake_drop_db() -> None:
        Recorder.called = True

    monkeypatch.setattr('api.mongo_orm.drop_db', fake_drop_db)
    result = runner.invoke(args=['drop-db'])
    assert 'is dropped' in result.output
    assert Recorder.called
