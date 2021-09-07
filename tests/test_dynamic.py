from dynamic import Dynamic
from pprint import pprint
import json
from data_helper import DATA_FOLDER


def test_as_dynamic():
    items = [1, 'abc', None, {'k': 'value', 'complexed': {'a': 1, 'b': None}}]
    d = Dynamic.as_dynamic(items)
    pprint(d)
    pprint(d[0])
    pprint(d[1])
    pprint(d[3])


def test_get():
    obj = Dynamic.from_json('{"color": "white", "category": "value", "code": {"rgba": [0, 0, 0, 1], "hex": "#FFF"} }')
    assert obj.code.HEx == '#FFF'
    assert obj.code.RGBA[3] == 1


def test_from_json():
    file_path = str(DATA_FOLDER.joinpath('colors.json'))
    obj = Dynamic.from_json(file_path)
    pprint(json.dumps(obj))
    red = obj[2]
    pprint(red)
    red2 = obj.__getattr__("[2]")
    pprint(red2)


def test_deep_update():
    obj = Dynamic.from_json('{"color": "white", "category": "value", "code": {"rgba": [0, 0, 0, 1], "hex": "#FFF"} }')
    udt = Dynamic.from_json('{ "code": { "hex": "#FFFFFF" } }')
    updated = Dynamic.update_deep(obj, udt)
    pprint(json.dumps(updated))
