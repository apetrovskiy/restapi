# -*- coding: utf-8 -*-
from datetime import date
from typing import Mapping, Iterable, Any, Dict, List

from numpy import percentile

from api.citizen_schema import Citizen


def calc_birthdays(citizens_data: Mapping[int, Citizen]
                   ) -> Mapping[str, Iterable[Mapping[str, int]]]:
    months: Dict[int, Dict[int, Dict[str, int]]] = {
        i: {} for i in range(1, 13)
    }

    for citizen_id, citizen in citizens_data.items():
        for relative_id in citizen.relatives:
            month = citizens_data[relative_id].birth_date.month

            try:
                months[month][citizen_id]["presents"] += 1
            except KeyError:
                months[month][citizen_id] = {
                    "citizen_id": citizen_id,
                    "presents": 1
                }

    return {str(i): list(months[i].values()) for i in range(1, 13)}


def calc_age_by_towns(
        citizens_data: Mapping[int, Citizen],
        percentils: Iterable[int] = (50, 75, 99)
                      ) -> Iterable[Mapping[str, Any]]:
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

    stats = []

    for town in towns:
        stat = {"town": town}

        for pv in percentils:
            stat[f"p{pv}"] = round(
                percentile(towns[town], pv, interpolation='linear'), 2
            )

        stats.append(stat)

    return stats
