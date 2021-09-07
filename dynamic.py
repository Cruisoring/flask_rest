from __future__ import annotations
import collections
from typing import Tuple, Any, List, Dict, Optional, Union, Iterable
import json


class Dynamic(dict):
    """Python version of dynamic object in .NET.

    It would expose the keys of underlying dict as attributes for easier read/write.
    When self.case_ignored is set to True, then case-insensitive matching would be used to locate
    the item when there is no exacting matching found.

    TODO: how to handle the keys imported from another dict when they are case-insensitive equal?
    """

    KEY_SEPERATOR = '.'
    CASE_IGNORED = True

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.__getattr__(str(key))
        else:
            return self.__getattr__(key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            # super().__setitem__(str(key), value)
            self.__setattr__(str(key), value)
        else:
            # super().__setitem__(key, value)
            self.__setattr__(key, value)


    def __getattr__(self, key):
        if key in self:
            return super().get(key)
        elif key[0] == '[' and key[-1] == ']':
            index = key[1:len(key)-1]
            return super().get(index)

        if not isinstance(key, str) or not Dynamic.CASE_IGNORED:
            return None

        matched = next((k for k in self.keys() if k.lower() == key.lower()), None)
        if matched is not None:
            return super().get(matched)
        elif Dynamic.KEY_SEPERATOR not in key:
            return None 

        key_paths = key.split(Dynamic.KEY_SEPERATOR)
        current = self
        for p in key_paths:
            current = current.__getattr__(p)
            if current is None:
                return None

        return current

    def __setattr__(self, key, value):
        if key in self:
            # self[key] = value
            super().__setitem__(key, value)
        elif Dynamic.CASE_IGNORED:
            matched = [k for k in self.keys() if str(k).lower() == key.lower()]
            if len(matched) == 1:
                # self[matched[0]] = value
                super().__setitem__(matched[0], value)
            elif len(matched) == 0:
                # self[key] = value
                super().__setitem__(key, value)
            else:
                dup = ', '.join(matched)
                msg = f'Multiple matchings: {dup}'
                raise NotImplementedError(msg)
        else:
            # self[key] = value
            super().__setitem__(key, value)

    def __delattr__(self, key):
        if key in self.keys():
            del self[key]
        elif self.case_insensitive:
            matched = next((k for k in self.keys() if k.lower() == key.lower()), None)
            if matched:
                del self[matched]
            else:
                raise AttributeError(f'No attribute similar to {key}')
        else:
            raise AttributeError(f'No attribute of {key}')

    def __dir__(self) -> Iterable[str]:
        return self.keys()

    # def __call__(self, *args, **kwargs):
    #     return Dynamic.as_dynamic(**kwargs)

    # def update(self, new_values: Dict):
    #     return update_deep(self, new_values)


    @classmethod
    def as_dynamic(cls, obj: Union[Dict, List, Dynamic]):
        if isinstance(obj, Dynamic):
            return obj

        d = Dynamic()
        if isinstance(obj, dict):
            for k, v in obj.items():
                d.__setattr__(k, cls.as_dynamic(v))
            # d.update(items)
            return d
        elif isinstance(obj, list):
            l = [cls.as_dynamic(d) for d in obj]
            d = cls.update_deep(d, l)
            return d
        else:
            return obj

    @classmethod
    def update_deep(cls, d1, d2):

        result = Dynamic.as_dynamic(d1)

        if isinstance(d2, Dict):
            for k, v in d2.items():
                if not k in result:
                    result[k] = cls.as_dynamic(v)
                elif isinstance(result[k], Dict):
                    if isinstance(v, collections.Mapping):
                        result[k] = cls.update_deep(result[k], v)
                    else:
                        raise NotImplementedError()
                else:
                    result[k] = cls.as_dynamic(v)
        elif isinstance(d2, List):
            for k, v in enumerate(d2):
                # result.__setattr__(k, v)
                result.__setattr__(str(k), v)
            # result = {str(k): v for }
            # result = cls.update_deep(result, indexed)
        else:
            raise NotImplementedError()

        return result

    
    @classmethod
    def from_json(cls, json_obj: str) -> Union(None, Dynamic):
        
        try:
            if json_obj.endswith('.json'):
                with open(json_obj) as json_file:
                    data = json.load(json_file)
                    data = Dynamic.as_dynamic(data)
            else:
                data = json.loads(json_obj)
                data = Dynamic.as_dynamic(data)
            return data
        except Exception as ex:
            if hasattr(ex, 'message'):
                print(ex.message)
            else:
                print(ex)
            return None

    @classmethod
    def as_keyed(cls, rows: List[Dict], key: str):
        if isinstance(rows, dict):
            return rows
        elif isinstance(rows, list):
            l = [cls.as_dynamic(d) for d in rows]
            return {row[key]: row for row in l}
        else:
            raise NotImplementedError()


