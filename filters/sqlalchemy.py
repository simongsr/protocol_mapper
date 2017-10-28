import inspect
from collections import OrderedDict

import itertools

from filters import core
from main import Field

__author__  = 'Simone Pandolfi'
__email__   = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


BUILDER_NAME   = __name__.split('.')[-1]
BUILDER_PREFIX = BUILDER_NAME + '__'

MODIFIERS      = {
    'backref': 'backref',
}


class Field:
    __slots__ = ('__field', )

    def __init__(self, field: Field):
        self.__field = field
        for name, func in ((n, f) for n, f in inspect.getmembers(field, predicate=inspect.ismethod) if not n.startswith('_')):
            print(name, func)
            setattr(self, name, lambda: func())


def modelname(model):
    return '__'.join(model['fullname'])


def datatype(field):
    DATA_TYPES = {
        'double'   : 'Float',
        'float'    : 'Float',
        'int32'    : 'Integer',
        'int64'    : 'BigInteger',
        'uint32'   : 'Integer',
        'uint64'   : 'BigInteger',
        'sint32'   : 'Integer',
        'sint64'   : 'BigInteger',
        'fixed32'  : 'Integer',
        'fixed64'  : 'BigInteger',
        'sfixed32' : 'Integer',
        'sfixed64' : 'BigInteger',
        'int'      : 'Integer',
        'long'     : 'BigInteger',
        'date'     : 'Date',
        'timestamp': 'DateTime',
        'time'     : 'Time',
        'bool'     : 'Boolean',
        'string'   : 'String',
        'bytes'    : 'LargeBinary',
    }
    datatype_ = field['data_type']
    if isinstance(datatype_, dict) and datatype_['type'] == 'model':
        return "'" + '__'.join(datatype_['fullname']) + "'"
    if isinstance(datatype_, str) and datatype_ in DATA_TYPES:
        return DATA_TYPES[datatype_]
    raise TypeError('Unknown data type: {0}'.format(datatype_))


def column_constraints(field):
    return ('{0}={1}'.format(MODIFIERS.get(k, k), ''.join(v)) for k, v in field['modifiers'].items() if k in MODIFIERS or k.startswith(BUILDER_PREFIX))


def column_constraints_count(field):
    i = 0
    for c in column_constraints(field):
        i += 1
    return i


def association_tablename(field):
    return 'association_table___{0}___{1}'.format(modelname(field['parent']), modelname(field['data_type']))


def association_foreignkeys_dict(field):

    def kv(f, m):
        model_name = modelname(m)  #field['parent'])
        field_name = f['name']
        return "'{0}___{1}'".format(model_name, field_name), "'{0}.{1}'".format(model_name, field_name)

    parent_keyfields   = [kv(keyfield, field['parent']) for keyfield in core.key_fields(field['parent'])]
    datatype_keyfields = [kv(keyfield, field['data_type']) for keyfield in core.key_fields(field['data_type'])]
    return OrderedDict(itertools.chain(parent_keyfields, datatype_keyfields))



FILTERS = {
    'sqlalchemy.modelname'                   : modelname,
    'sqlalchemy.datatype'                    : datatype,
    'sqlalchemy.column_constraints'          : column_constraints,
    'sqlalchemy.column_constraints_count'    : column_constraints_count,
    'sqlalchemy.association_tablename'       : association_tablename,
    'sqlalchemy.association_foreignkeys_dict': association_foreignkeys_dict,
}
