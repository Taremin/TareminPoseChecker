import bpy
import json
import re


def print(*args):
    pass


def _read_walkdown(obj, depth=0):
    if depth > 10:
        return None
    if obj is None:
        return {
            "type": "property",
            "value": obj
        }
    elif isinstance(obj, str):
        return {
            "type": "property",
            "value": obj
        }
    elif isinstance(obj, bpy.types.ID):
        return {
            "type": "object",
            "value": obj.name,
            "location": re.split('[\.\[\]]+', repr(obj))[2]
        }
    elif hasattr(obj, "items"):
        out = {}
        for i, j in obj.items():
            out[i] = _read_walkdown(j, depth+1)
        return {
            "type": "attribute",
            "value": out
        }
    elif hasattr(obj, "__iter__"):
        out = []
        for i in obj:
            out.append(_read_walkdown(i, depth+1))
        return {
            "type": "collection",
            "value": out
        }
    else:
        return {
            "type": "property",
            "value": obj
        }


def property_to_json(property):
    return json.dumps(_read_walkdown(property), ensure_ascii=False)


def _merge_walkdown(prev_obj, attribute_name, json_obj, path=[], depth=0):
    type = json_obj["type"]
    value = json_obj["value"]

    if type == "attribute":
        for key, val in value.items():
            if hasattr(val, "items"):
                if isinstance(attribute_name, int):
                    property = prev_obj[attribute_name]
                else:
                    property = getattr(prev_obj, attribute_name)

                _merge_walkdown(property, key, val, path +
                                [".%s" % key], depth+1)

    elif type == "collection":
        property = getattr(prev_obj, attribute_name)
        property.clear()
        for i, item in enumerate(value):
            tmp = property.add()
            _merge_walkdown(property, i, item, path + ["[%d]" % i], depth+1)
    elif type == "object":
        val = getattr(bpy.data, json_obj["location"])[value]
        print("\t"*depth, "Path:", "".join(path), "=", val)
        print("\t"*depth, "Set:", prev_obj, attribute_name, value)
        if isinstance(attribute_name, int):
            prev_obj[attribute_name] = val
        else:
            setattr(prev_obj, attribute_name, val)
    elif type == "property":
        print("\t"*depth, "Path:", "".join(path), "=", value)
        print("\t"*depth, "Set:", prev_obj, attribute_name, value)
        if isinstance(attribute_name, int):
            prev_obj[attribute_name] = value
        else:
            setattr(prev_obj, attribute_name, value)


def json_to_property(property, json_str):
    print("JSON -> Property")
    json_obj = json.loads(json_str)
    print("JSON:", json_obj)
    for key, value in property.bl_rna.properties.items()[2:]:
        print("Key:", key)
        if key in json_obj["value"]:
            _merge_walkdown(property, key, json_obj['value'][key])
    print("JSON -> Property Finished")


def clear_property(settings):
    for key, value in settings.items():
        if isinstance(value, int):
            setattr(settings, key, 0)
        elif isinstance(value, list):
            getattr(settings, key).clear()
        elif isinstance(value, str):
            setattr(settings, key, "")
        else:
            print("unknown type:", value.__class__)
