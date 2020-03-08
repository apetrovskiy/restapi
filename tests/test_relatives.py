from typing import Mapping

import pytest

from tests import change_relatives_to
from api.citizen_schema import ValidationError, Citizen


def test_add_relatives(data3d: Mapping[int, Citizen]) -> None:
    citizens = change_relatives_to(data3d, 3, [1, 2])

    assert citizens[1].relatives == [2, 3]
    assert citizens[2].relatives == [1, 3]
    assert 3 not in citizens.keys()


def test_rem_relatives(data3d: Mapping[int, Citizen]) -> None:
    citizens = change_relatives_to(data3d, 1, [])

    assert 1 not in citizens.keys()
    assert citizens[2].relatives == []
    assert 3 not in citizens.keys()


def test_unexisted_relative(data3d: Mapping[int, Citizen]) -> None:
    with pytest.raises(ValidationError):
        change_relatives_to(data3d, 1, [42])
