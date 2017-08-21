#!/usr/bin/env python3.5
from collections import OrderedDict

from filters import core

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
    'max_length',
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
    BUILDER_PREFIX + 'max_length',
    BUILDER_PREFIX + 'related_name',
)


def class_name(obj):
    if not isinstance(obj, dict):
        raise TypeError("Obj must be an instance of a model, a message or a field, got: {0}".format(obj))

    if obj['type'] == 'field':
        return '_nested_'.join((class_name(obj['parent']), core.upper_camel_case(obj['name'])))
    return core.upper_camel_case(obj['fullname'], splitstr='_nested_')


def prepare_args(modifiers):
    if not isinstance(modifiers, dict):
        raise TypeError('Expected modifiers was a dict, got: {0}'.format(type(modifiers).__name__))
    args = []
    if 'key' in modifiers:
        modifiers['primary_key'] = True
    for key, value in modifiers.items():
        if key in MODIFIERS:
            if key.startswith(BUILDER_PREFIX):
                key = key[len(BUILDER_PREFIX):]
            if isinstance(value, list):
                value = value[-1]
            if value == '__NOW__':
                value = 'django.utils.timezone.now'
            args.append('{0}={1}'.format(key, value))
    return args


def field_declaration(field):
    if not isinstance(field, dict) or field['type'] != 'field':
        raise TypeError('Expected a field object, got: [{0}] {1}'.format(type(field).__name__, field))

    struct   = 'models.{fieldtype}({args})'
    datatype = field['data_type']

    def make_single_raw_type(field):
        fieldtype = FIELD_MAPPING[datatype]
        args      = OrderedDict(field['modifiers'])
        if field['multiplicity'] == 'required':
            args['blank'] = False
        args      = ', '.join(prepare_args(args))
        return struct.format(fieldtype=fieldtype, args=args)

    def make_repeated_raw_type(field):
        args = OrderedDict(field['modifiers'])
        if field['multiplicity'] == 'required':
            args['blank'] = False
        modelname = class_name(field)  # '{0}{1}'.format(''.join(field['parent']['fullname']), field['name'])
        return struct.format(fieldtype='ManyToManyField', args=modelname)

    def make_single_model_type(field):
        args = OrderedDict(field['modifiers'])
        if field['multiplicity'] == 'required':
            args['blank'] = False
        ref_model = class_name(datatype)
        ref_model = ref_model if ref_model == 'User' else "'{0}'".format(ref_model)
        args = ', '.join([ref_model] + prepare_args(args))
        if field['modifiers'].get('python_django__one_to_one', False):
            return struct.format(fieldtype='OneToOneField', args=args)
        return struct.format(fieldtype='ForeignKey', args=args)

    def make_repeated_model_type(field):
        args = OrderedDict(field['modifiers'])
        if field['multiplicity'] == 'required':
            args['blank'] = False
        ref_model = class_name(datatype)
        ref_model = ref_model if ref_model == 'User' else "'{0}'".format(ref_model)
        args = ', '.join([ref_model] + prepare_args(args))
        return struct.format(fieldtype='ManyToManyField', args=args)

    if isinstance(datatype, str) and datatype in FIELD_MAPPING:
        if field['multiplicity'] in ('optional', 'required'):
            return make_single_raw_type(field)
        else:
            return make_repeated_raw_type(field)
    elif isinstance(datatype, dict) and datatype['type'] == 'model':
        if field['multiplicity'] in ('optional', 'required'):
            return make_single_model_type(field)
        else:
            return make_repeated_model_type(field)
    elif isinstance(datatype, dict) and datatype['type'] == 'enum':
        raise NotImplementedError('Repeated enums are not supported yet')
    raise Exception('Unknown field type: {0} {1} {2}'.format(
        field['multiplicity'], type(datatype).__name__, field['name']))


def map_data_type(datatype):
    if not isinstance(datatype, str):
        raise TypeError('Datatype must be a string, got: {0}'.format(type(datatype).__name__))
    if datatype not in FIELD_MAPPING:
        raise Exception('Unknown data type: {0}'.format(datatype))
    return FIELD_MAPPING[datatype]


FILTERS = {
    'python_django.class_name'       : class_name,
    'python_django.prepare_args'     : prepare_args,
    'python_django.field_declaration': field_declaration,
    'python_django.map_data_type'    : map_data_type,
}
