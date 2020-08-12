from typing import List

from bson import ObjectId

from api.schema import CitizenId, PrettyCitizens, update_relatives


def import_id(post_response) -> ObjectId:
    return post_response.json()["data"]["import_id"]


def change_relatives_to(
        citizens: PrettyCitizens,
        citizen_id: CitizenId,
        relatives: List[CitizenId]
) -> PrettyCitizens:
    different_citizens = update_relatives(
        relatives, citizens[citizen_id].relatives, citizens, citizen_id
    )

    return different_citizens
