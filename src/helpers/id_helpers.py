from bson import ObjectId


def parse_id(id: str) -> int | ObjectId:
    if ObjectId.is_valid(id):
        return ObjectId(id)
    elif id.isdigit():
        return int(id)
    raise RuntimeError("Id must be of type int or ObjectId")


def is_valid_id(id: str) -> bool:
    return ObjectId.is_valid(id) or id.isdigit()
