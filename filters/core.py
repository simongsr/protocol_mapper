#!/usr/bin/env python3.5

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


FILTERS = {
    'core.enums'        : enums,
    'core.root_models'  : root_models,
    'core.nested_models': nested_models,
    'core.models'       : models,
}
