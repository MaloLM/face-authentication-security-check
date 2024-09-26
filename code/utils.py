import json


def get_value_from_json(file_path, key):
    with open(file_path, 'r') as f:
        data = json.load(f)

    if key in data:
        return data[key]
    else:
        return None
