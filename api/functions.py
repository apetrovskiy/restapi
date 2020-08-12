from datetime import date
from typing import Dict, List

from numpy import percentile

from api.schema import (AgeStatResponse, BirthdaysResponse, CitizenId,
                        PrettyCitizens)


def calc_birthdays(citizens_data: PrettyCitizens) -> BirthdaysResponse.Year:
    """
    Возвращает жителей и количество подарков, которые они будут покупать своим
    ближайшим родственникам (1-го порядка), сгруппированных по месяцам.
    """
    months: Dict[int, Dict[
                           CitizenId,
                           BirthdaysResponse.Year.PresentsCounter
    ]] = {
        month: {} for month in range(1, 13)
    }

    for citizen_id, citizen in citizens_data.items():
        for relative_id in citizen.relatives:
            month = citizens_data[relative_id].birth_date.month

            try:
                months[month][citizen_id].presents += 1
            except KeyError:
                months[month][citizen_id] = BirthdaysResponse.Year.\
                    PresentsCounter(
                    citizen_id=citizen_id,
                    presents=1
                )

    presents = BirthdaysResponse.Year(**{
        str(month): list(
            months[month].values()
        ) for month in range(1, 13)
    })

    return presents


def calc_age_by_towns(
    citizens_data: PrettyCitizens
) -> List[AgeStatResponse.TownStat]:
    """
    Возвращает статистику по городам для указанного набора данных в разрезе
    возраста (полных лет) жителей: p50, p75, p99, где число - это значение
    перцентиля.
    """
    towns: Dict[str, List[int]] = {}

    for citizen in citizens_data.values():
        birth_date = citizen.birth_date
        today = date.today()
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age = today.year - birth_date.year - 1
        else:
            age = today.year - birth_date.year

        try:
            towns[citizen.town].append(age)
        except KeyError:
            towns[citizen.town] = [age]

    stats = [
        AgeStatResponse.TownStat(
            town=town,
            p50=round(
                percentile(towns[town], 50, interpolation='linear'), 2
            ),
            p75=round(
                percentile(towns[town], 75, interpolation='linear'), 2
            ),
            p99=round(
                percentile(towns[town], 99, interpolation='linear'), 2
            )
        ) for town in towns
    ]

    return stats
