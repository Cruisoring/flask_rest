import json
import csv
import decimal
from datetime import datetime
from dynamic import Dynamic
from pathlib import Path
from typing import Tuple, Any, List, Dict, Optional, Union

DATA_FOLDER = Path(__file__).parent / 'data'

DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

DATETIME_FORMATS = sorted(['%d-%m-%Y %H:%M:%S', '%d-%b-%Y %H:%M:%S',
                           '%Y-%m-%d %H:%M:%S', '%Y-%b-%d %H:%M:%S',
                           "%d/%m/%Y", "%d/%m/%y"],
                          key=len, reverse=True)

def as_datetime(d):
    for f in DATETIME_FORMATS:
        try:
            return datetime.strptime(d, f)
        except (ValueError, SyntaxError):
            continue
    else:
        raise ValueError(f"Unsupported datetime str: {d}")


def save_content(file_name: str, content: str):
    path = Path(DATA_FOLDER, file_name)
    
    with open(path, mode='w', encoding='utf-8') as f:
        content = f.write(content)


def as_none(x):
    return x if x != 'NULL' else None


csv_value_funcs = [int,
                   float,
                   as_datetime,
                   as_none
                   ]


def try_convert(o):
    if o is None or o == '':
        return None

    for f in csv_value_funcs:
        try:
            return f(o)
        except (ValueError, SyntaxError):
            pass
    return o


def as_json_default(o):
    if isinstance(o, datetime.date):
        return o.strftime(DEFAULT_DATE_FORMAT)
    elif isinstance(o, datetime.datetime):
        if o.totla_seconds == 0:
            return o.strftime(DEFAULT_DATE_FORMAT)
        else:
            return o.strftime(DEFAULT_DATETIME_FORMAT)
    

def as_json(item):
    return json.dumps(item, default=as_json_default, indent=4, sort_keys=True)


def load_content(file_path):
    path = Path(DATA_FOLDER, file_path)

    if not path.exists():
        return None
    
    with open(path, encoding='utf-8-sig') as file:
        content = file.read()
        return content


def load_csv(file_path: str, key: str = None) -> Dynamic:

    if isinstance(file_path, str):
        file_path = DATA_FOLDER.joinpath(file_path)
    if not file_path.exists():
        return None

    with open(file_path, encoding='utf-8-sig') as file:
        rows = [{k: v for k, v in row.items()} for row in csv.DictReader(file, skipinitialspace=True)]
        rows = [Dynamic(row) for row in rows]

        if key is None:
            return Dynamic.as_dynamic(rows)
    
        dicts = {str(row[key]): row for row in rows}
        return Dynamic.as_dynamic(dicts)


def load_json(file_path: str, key: str = None) -> Dynamic:

    if isinstance(file_path, str):
        file_path = DATA_FOLDER.joinpath(file_path)
    if not file_path.exists():
        return None

    with open(file_path) as json_file:
        try:
            data = json.load(json_file)
            if isinstance(data, List) and key is not None:
                data = {str(item[key]): item for item in data}
            data = Dynamic.as_dynamic(data)
            return data
        except Exception:
            return None


def load(file_path: str, key: str = None) -> Dynamic:

    file_path = DATA_FOLDER.joinpath(file_path)
    if not file_path.exists():
        return None
    if file_path.suffix.lower() == '.csv':
        return load_csv(file_path, key)
    elif file_path.suffix.lower() == '.json':
        return load_json(file_path, key)
    else:
        raise NotImplementedError(f'Not supported suffix: {file_path}')
    


class SRGJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%d/%m/%Y")
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return float(o)

        return json.JSONEncoder.default(self, o)


def save_json(obj: Any, file_path: Path) -> None:
    try:
        with open(DATA_FOLDER.joinpath(file_path), 'w') as fh:
            json_str = json.dumps(obj, indent=2, cls=SRGJsonEncoder)
            json_str = json_str.replace('NaN', '"NaN"')
            fh.write(json_str)
        print(f'{DATA_FOLDER.joinpath(file_path)} saved')
    except Exception as ex:
        print(f'Failed to save JSON object to {DATA_FOLDER.joinpath(file_path)}: {ex}')