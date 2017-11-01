#!/usr/bin/env python3.5
from collections import OrderedDict

import re

from main import DATA_TYPES, Field

__author__  = 'Simone Pandolfi'
__email__   = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


# def upper_camel_case(name, splitstr='_'):
#     if not isinstance(name, (str, list)):
#         raise TypeError("Name must be a string or a list, got: {0} ({1})".format(name, type(name).__name__))
#     if isinstance(name, list):
#         return splitstr.title().join(n.title().replace('_', '') for n in name)
#     return name.title().replace('_', '')


# def lower_camel_case(name, joistr='_'):
#     if len(name) > 0:
#         name = upper_camel_case(name, joistr=joistr)
#         return name[0].lower() + name[1:]
#     return ''


# def enums(obj):
#     if not isinstance(obj, dict) or 'objects' not in obj:
#         raise Exception("Expected 'env' was a valid environment, model or message instance")
#
#     return (enum for enum in obj['objects'].values() if enum['type'] == 'enum')


# def root_models(env):
#     if not isinstance(env, dict) or 'objects' not in env:
#         raise Exception("Expected 'env' was a valid environment instance")
#
#     return (obj for obj in env['objects'].values() if obj['type'] == 'model')


# def nested_models(model):
#     if not isinstance(model, dict) or model['type'] != 'model':
#         raise Exception("Expected 'model' was a valid model instance")
#
#     for _model in (obj for obj in model['objects'].values() if obj['type'] == 'model'):
#         yield _model
#         yield from nested_models(_model)


# def models(env, reverse=False):
#     if not isinstance(env, dict) or 'objects' not in env:
#         raise Exception("Expected 'env' was a valid environment instance")
#
#     for root_model in root_models(env):
#         if not reverse:
#             yield from nested_models(root_model)
#         yield root_model
#         if reverse:
#             yield from nested_models(root_model)


# def root_messages(env):
#     if not isinstance(env, dict) or 'objects' not in env:
#         raise Exception("Expected 'env' was a valid environment instance")
#
#     return (obj for obj in env['objects'].values() if obj['type'] == 'message')


# def nested_messages(message):
#     if not isinstance(message, dict) or message['type'] != 'message':
#         raise Exception("Expected 'message' was a valid message instance")
#
#     for _message in (obj for obj in message['objects'].values() if obj['type'] == 'message'):
#         yield _message
#         yield from nested_messages(_message)


# def messages(env):
#     if not isinstance(env, dict) or 'objects' not in env:
#         raise Exception("Expected 'env' was a valid environment instance")
#
#     for root_message in root_messages(env):
#         yield from nested_messages(root_message)
#         yield root_message


# def map_message_field_to_model(message):
#     if not isinstance(message, dict) or message['type'] != 'message':
#         raise Exception("Expected 'message' was a valid message instance")
#
#     models = OrderedDict()
#     for field in message['fields'].values():
#         if field['id'] is not None:
#             key = '.'.join(field['model_field']['parent']['fullname'])
#             models.setdefault(key, []).append(field)
#     return models


# def map_default_value(datatype):
#     if not isinstance(datatype, str) or datatype not in DATA_TYPES:
#         raise TypeError("Expected datatype was a row type, got: {0} ({1})".format(datatype, type(datatype).__name__))
#     return DATA_TYPES[datatype]


# def version(obj):
#
#     def field_version(field):
#         return int(field['modifiers'].get('version', 1))
#
#     def model_version(model):
#         return max(1, *(field_version(field) for field in model['fields'].values()))
#
#     if 'type' in obj:
#         if obj['type'] == 'model':
#             return model_version(obj)
#         elif obj['type'] == 'field':
#             return field_version(obj)
#         else:
#             raise TypeError('Unknown object type: {0}'.format(obj))
#     return max(1, *(model_version(model) for model in models(obj)))


# def enum_value(value):
#     if isinstance(value, (list, tuple)):
#         return value[0]
#     return value


# def extract_string_value(string):
#     if not isinstance(string, str):
#         raise TypeError('Expected string was a valid string, got: {0}'.format(string))
#
#     match = re.match(r'^"(.*?)"$|^\'(.*?)\'$', string)
#     if match is not None:
#         m1, m2 = match.groups()
#         return m1 if m1 is not None else m2
#     return string


# def build_uri(collection, vars):
#     if not isinstance(collection, (tuple, list)):
#         raise TypeError("Expected collection was a collection, got: {0} ({1})".format(collection, type(collection).__name__))
#     if not isinstance(vars, dict):
#         raise TypeError("Expected vars was a map, got: {0} ({1})".format(vars, type(vars).__name__))
#
#     def scan(lst):
#         ret = []
#         for item in lst:
#             if isinstance(item, (tuple, list)):
#                 ret += scan(item)
#             else:
#                 var = vars.get(item, item)
#                 if isinstance(var, (tuple, list)):
#                     ret += scan(var)
#                 else:
#                     ret.append(var if not isinstance(var, str) else extract_string_value(var))
#         return ret
#
#     return ''.join(scan(collection))


# def endpoints(schema):
#     if not isinstance(schema, dict) or 'endpoints' not in schema:
#         raise Exception("Expected 'schema' was a valid schema instance")
#     return (obj for obj in schema['endpoints'].values() if obj['type'] == 'endpoint')


def is_raw_type(field: Field) -> bool:
    if not isinstance(field, Field):
        raise TypeError('Expected a field object, got: {0}'.format(field))
    if not isinstance(field.datatype, str):
        return False
    return field.datatype in DATA_TYPES


# def key_fields(model):
#     return (f for f in model['fields'].values() if f['multiplicity'] == 'required' and 'key' in f['modifiers'] and is_raw_type(f))



FILTERS = {
    # 'core.upper_camel_case'          : upper_camel_case,
    # 'core.lower_camel_case'          : lower_camel_case,
    # 'core.enums'                     : enums,
    # 'core.root_models'               : root_models,
    # 'core.nested_models'             : nested_models,
    # 'core.models'                    : models,
    # 'core.root_messages'             : root_messages,
    # 'core.nested_messages'           : nested_messages,
    # 'core.messages'                  : messages,
    # 'core.map_message_field_to_model': map_message_field_to_model,
    # 'core.map_default_value'         : map_default_value,
    # 'core.version'                   : version,
    # 'core.extract_string_value'      : extract_string_value,
    # 'core.enum_value'                : enum_value,
    # 'core.build_uri'                 : build_uri,
    # 'core.endpoints'                 : endpoints,
    'core.is_raw_type'               : is_raw_type,
    # 'core.key_fields'                : key_fields,
}

