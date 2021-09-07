from __future__ import annotations
from datetime import datetime
from data_helper import load, as_json
from pathlib import Path
from flask import abort, request, Flask
import json
from dynamic import Dynamic

Mockings = {}
ITEM_METHODS = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH']
DEFAULT_API_ROUTE_PREFIX = "/api/"
DYNAMIC_ROUTES = {}

class Mock(object):
    """
    Mocking services with given source JSON/CSV file and route.
    """

    def __init__(self, source: str, keyname: str =None, route: str=None):
        self.source = source
        path = Path(source)
        self.route = DEFAULT_API_ROUTE_PREFIX + (route or path.stem)
        self.keyname = keyname or 'key'
        self.records = load(source, keyname)
        Mockings[self.route] = self
        self.last_update = datetime.now()

    def handle_all(self):
        return Mock.all(self.records)


    def handle_single(self, key):
        return Mock.mock(key, self.records, self.keyname)

    def handle(self, path: str):
        segments = path.split('/')
        if len(segments) == 1:
            if request.method in ['POST', 'DELETE', 'PUT', 'PATCH']:
                abort(400)
            else:
                return self.handle_all()
        elif len(segments) == 2:
            return self.handle_single(segments[1])
        else:
            raise NotImplementedError()


    def add_route(self, app, all_name: str=None, item_name: str=None):
        app.add_url_rule(self.route, all_name or self.route, self.handle_all)
        r = f"{self.route}/<key>"
        app.add_url_rule(r, item_name or r, self.handle_single, methods=ITEM_METHODS)


    @classmethod
    def all(cls, records):
        if request.args:
            f_string = ' and '.join([f'str(x.{k}) == "{v}"' for k, v in request.args.items()])
            condition = lambda x: eval(f_string)
            selected = []
            for item in records.values():
                if (condition(item)):
                    selected.append(item)
            return as_json(selected)
        else:
            return as_json([*records.values()])


    @classmethod
    def mock(cls, key, records, keyname):
        item = records[key]
        if request.method == 'GET':
            if item:
                return records[key], 200
            else:
                abort(404) 
        elif request.method == 'DELETE':
            if item:
                del records[key]
                return item, 202
            else:
                abort(404)
        elif request.method == 'PATCH':
            if item:
                payload = json.loads(request.data)
                patch = Dynamic.as_dynamic(payload)
                updated = Dynamic.update_deep(records[key], patch)
                records[key] = updated
                return updated, 202
            else:
                return 'No item to be patched.', 400

        payload = json.loads(request.data)
        new_item = Dynamic.as_dynamic(payload)
        if request.method == 'POST':
            if item:
                return records[key], 409
            else:
                records[key] = new_item
                return new_item, 201
        elif request.method == 'PUT':
            if item:
                records[key] = new_item
                return item, 202
            else:
                return 'No item to be replaced.', 400
        else:
            return f"Not supported method: {request.method}", 400
    

    @classmethod
    def add_mock(cls, app: Flask, source: str, keyname: str, route: str=None) -> Mock:
        mock = Mock(source, keyname, route)
        mock.add_route(app)
        return mock

    @classmethod
    def add_dynamic(cls, source: str, keyname: str, route: str=None) -> Mock:
       mock = Mock(source, keyname, route)
       route = route or mock.route.replace(DEFAULT_API_ROUTE_PREFIX, '')
       DYNAMIC_ROUTES[route] = mock
       return f"{mock.route} added as a dynamic route", 200

    @classmethod
    def handle_default(cls, path):
        route = path.split('/')[0]
        if route in DYNAMIC_ROUTES:            
            return DYNAMIC_ROUTES[route].handle(path)
        else:
            abort(400)
        

    