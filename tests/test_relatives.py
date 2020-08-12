import pytest

from api.schema import CitizenId
from tests import change_relatives_to


def test_add_relatives(pretty_citizens):
    citizens = change_relatives_to(
        pretty_citizens,
        CitizenId(3),
        [CitizenId(1), CitizenId(2)]
    )

    assert citizens[CitizenId(1)].relatives == [2, 3]
    assert citizens[CitizenId(2)].relatives == [1, 3]
    assert CitizenId(3) not in citizens.keys()


def test_rem_relatives(pretty_citizens):
    citizens = change_relatives_to(pretty_citizens, CitizenId(1), [])

    assert 1 not in citizens.keys()
    assert citizens[CitizenId(2)].relatives == []
    assert 3 not in citizens.keys()


def test_unexisted_relative(pretty_citizens):
    with pytest.raises(ValueError):
        change_relatives_to(pretty_citizens, CitizenId(1), [CitizenId(42)])
