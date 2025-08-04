from bson import ObjectId


def parse_id(id: str) -> int | ObjectId:
    try:
        if ObjectId.is_valid(id):
            return ObjectId(id)
        elif id.isdigit():
            return int(id)
        raise RuntimeError("Id must be of type int or ObjectId")
    except RuntimeError as e:
        raise e


def is_valid_id(id: str) -> bool:
    return ObjectId.is_valid(id) or id.isdigit()
