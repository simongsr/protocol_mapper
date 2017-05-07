#!/usr/bin/env python3.5

__author__ = 'Simone Pandolfi'
__email__ = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


FIELD_MAPPING  = {
    'double'   : 'float',
    'float'    : 'float',
    'int32'    : 'int',
    'int64'    : 'int',
    'uint32'   : 'int',
    'uint64'   : 'int',
    'sint32'   : 'int',
    'sint64'   : 'int',
    'fixed32'  : 'int',
    'fixed64'  : 'int',
    'sfixed32' : 'int',
    'sfixed64' : 'int',
    'int'      : 'int',
    'long'     : 'int',
    'date'     : 'date',
    'timestamp': 'datetime',
    'time'     : 'time',
    'bool'     : 'bool',
    'string'   : 'str',
    'bytes'    : 'byte',
}


def map_data_type(datatype):
    if not isinstance(datatype, str):
        raise TypeError("Datatype must be a string, got: {0}".format(type(datatype).__name__))
    if datatype not in FIELD_MAPPING:
        raise Exception('Unknown data type: {0}'.format(datatype))
    return FIELD_MAPPING[datatype]


FILTERS = {
    'python.map_data_type': map_data_type,
}
