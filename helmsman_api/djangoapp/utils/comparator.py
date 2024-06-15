import json
from deepdiff import DeepDiff


def to_dict(data):
    if isinstance(data, str):
        return json.loads(data)
    elif isinstance(data, dict):
        return data
    else:
        raise ValueError("Unsupported data type")


def compare_json(data1, data2):
    dict1 = to_dict(data1)
    dict2 = to_dict(data2)

    diff = DeepDiff(dict1, dict2)

    return diff == {}
