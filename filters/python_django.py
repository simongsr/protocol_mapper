#!/usr/bin/env python3.5
from collections import OrderedDict

__author__  = 'Simone Pandolfi'
__email__   = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


BUILDER_NAME   = __name__.split('.')[-1]
BUILDER_PREFIX = BUILDER_NAME + '__'


FIELD_MAPPING  = {
    'double'   : 'FloatField',
    'float'    : 'FloatField',
    'int32'    : 'IntegerField',
    'int64'    : 'IntegerField',
    'uint32'   : 'IntegerField',
    'uint64'   : 'IntegerField',
    'sint32'   : 'IntegerField',
    'sint64'   : 'IntegerField',
    'fixed32'  : 'IntegerField',
    'fixed64'  : 'IntegerField',
    'sfixed32' : 'IntegerField',
    'sfixed64' : 'IntegerField',
    'int'      : 'IntegerField',
    'long'     : 'IntegerField',
    'date'     : 'DateField',
    'timestamp': 'DateTimeField',
    'time'     : 'TimeField',
    'bool'     : 'BooleanField',
    'string'   : 'CharField',
    'bytes'    : 'BinaryField',
}

MODIFIERS      = (
    'null',
    'blank',
    'default',
    'choices',
    'primary_key',
    'unique',
    BUILDER_PREFIX + 'null',
    BUILDER_PREFIX + 'blank',
    BUILDER_PREFIX + 'choices',
    BUILDER_PREFIX + 'db_column',
    BUILDER_PREFIX + 'db_index',
    BUILDER_PREFIX + 'db_tablespace',
    BUILDER_PREFIX + 'default',
    BUILDER_PREFIX + 'editable',
    BUILDER_PREFIX + 'error_messages',
    BUILDER_PREFIX + 'help_text',
    BUILDER_PREFIX + 'primary_key',
    BUILDER_PREFIX + 'unique',
    BUILDER_PREFIX + 'unique_for_date',
    BUILDER_PREFIX + 'unique_for_month',
    BUILDER_PREFIX + 'unique_for_year',
    BUILDER_PREFIX + 'verbose_name',
    BUILDER_PREFIX + 'validators',
)


def field_declaration(field):
    if not isinstance(field, dict) or field['type'] != 'field':
        raise TypeError('Expected a field object, got: [{0}] {1}'.format(type(field).__name__, field))

    struct   = 'models.{fieldtype}({args})'
    datatype = field['data_type']

    def __make_args(**kwargs):
        args = []
        for key, value in kwargs.items():
            if key.startswith(BUILDER_PREFIX):
                key = key[len(BUILDER_PREFIX):]
            if isinstance(value, list):
                value = value[-1]
            args.append('{0}={1}'.format(key, value))

        return ', '.join(args)

    def make_single_raw_type(field):
        fieldtype = FIELD_MAPPING[datatype]
        args      = OrderedDict(field['modifiers'])
        if field['multiplicity'] == 'required':
            args['blank'] = False
        args      = __make_args(**args)
        return struct.format(fieldtype=fieldtype, args=args)

    def make_single_model_type(field):
        args = OrderedDict(field['modifiers'])
        if field['multiplicity'] == 'required':
            args['blank'] = False
        args = '{0}, {1}'.format('__'.join(datatype['fullname']), __make_args(**args))
        return struct.format(fieldtype='ForeignKey', args=args)

    if isinstance(datatype, str) and datatype in FIELD_MAPPING:
        if field['multiplicity'] in ('optional', 'required'):
            return make_single_raw_type(field)
    elif isinstance(datatype, dict) and datatype['type'] == 'model':
        if field['multiplicity'] in ('optional', 'required'):
            return make_single_model_type(field)
    else:
        return ''
    raise Exception('Unknown field type: {0} {1} {2}'.format(
        field['multiplicity'], type(datatype).__name__, field['name']))


FILTERS = {
    'python_django.field_declaration': field_declaration,
}
