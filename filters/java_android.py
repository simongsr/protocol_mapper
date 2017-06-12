#!/usr/bin/env python3.5
from filters import core

__author__ = 'Simone Pandolfi'
__email__ = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


def path_name(obj):
    return '__'.join(obj['fullname']).upper() + '_PATH'


def is_shared_pref_model(model):
    return model['modifiers'].get('shared_preferences_model', False) is True


def entry_name(model):
    return '__'.join(core.upper_camel_case(name) for name in model['fullname'])


def table_name(model):
    # return '__'.join(core.upper_camel_case(name) for name in model['fullname']).lower()
    return '__'.join(model['fullname']).lower()


def field_name(field):
    return 'COLUMN_' + field['name'].upper() + ('_ID' if isinstance(field['data_type'], dict) else '')


def column_name(field):
    return core.upper_camel_case(field['name']).lower() + ('_id' if isinstance(field['data_type'], dict) else '')


def index_name(field):
    return 'INDEX_' + field['name'].upper()


def fields(model, repeated=False):

    def include_repeated(field):
        return True if repeated else field['multiplicity'] != 'repeated'

    for field in model['fields'].values():
        if field['id'] >= 0 and \
                include_repeated(field) and \
                field['modifiers'].get('java_android__excempt', False) is False:
            yield field


def repeated_fields(model):
    for field in fields(model, repeated=True):
        if field['multiplicity'] == 'repeated':
            yield field


FILTERS = {
    'java_android.path_name'           : path_name,
    'java_android.is_shared_pref_model': is_shared_pref_model,
    'java_android.entry_name'          : entry_name,
    'java_android.table_name'          : table_name,
    'java_android.field_name'          : field_name,
    'java_android.column_name'         : column_name,
    'java_android.index_name'          : index_name,
    'java_android.fields'              : fields,
    'java_android.repeated_fields'     : repeated_fields,
}
