#!/usr/bin/env python3.5
from collections import OrderedDict

__author__  = 'Simone Pandolfi'
__email__   = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


def enums(obj):
    if not isinstance(obj, dict) or 'objects' not in obj:
        raise Exception("Expected 'env' was a valid environment, model or message instance")

    return (enum for enum in obj['objects'].values() if enum['type'] == 'enum')


def root_models(env):
    if not isinstance(env, dict) or 'objects' not in env:
        raise Exception("Expected 'env' was a valid environment instance")

    return (obj for obj in env['objects'].values() if obj['type'] == 'model')


def nested_models(model):
    if not isinstance(model, dict) or model['type'] != 'model':
        raise Exception("Expected 'model' was a valid model instance")

    for _model in (obj for obj in model['objects'].values() if obj['type'] == 'model'):
        yield _model
        yield from nested_models(_model)


def models(env):
    if not isinstance(env, dict) or 'objects' not in env:
        raise Exception("Expected 'env' was a valid environment instance")

    for root_model in root_models(env):
        yield root_model
        yield from nested_models(root_model)


def root_messages(env):
    if not isinstance(env, dict) or 'objects' not in env:
        raise Exception("Expected 'env' was a valid environment instance")

    return (obj for obj in env['objects'].values() if obj['type'] == 'message')


def nested_messages(message):
    if not isinstance(message, dict) or message['type'] != 'message':
        raise Exception("Expected 'message' was a valid message instance")

    for _message in (obj for obj in message['objects'].values() if obj['type'] == 'message'):
        yield _message
        yield from nested_messages(_message)


def messages(env):
    if not isinstance(env, dict) or 'objects' not in env:
        raise Exception("Expected 'env' was a valid environment instance")

    for root_message in root_messages(env):
        yield root_message
        yield from nested_messages(root_message)


def map_message_field_to_model(message):
    if not isinstance(message, dict) or message['type'] != 'message':
        raise Exception("Expected 'message' was a valid message instance")

    models = OrderedDict()
    for field in message['fields'].values():
        if field['id'] is not None:
            key = '.'.join(field['model_field']['model']['fullname'])
            models.setdefault(key, []).append(field)
    return models


FILTERS = {
    'core.enums'                     : enums,
    'core.root_models'               : root_models,
    'core.nested_models'             : nested_models,
    'core.models'                    : models,
    'core.root_messages'             : root_messages,
    'core.nested_messages'           : nested_messages,
    'core.messages'                  : messages,
    'core.map_message_field_to_model': map_message_field_to_model,
}
