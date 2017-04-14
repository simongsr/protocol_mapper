#!/usr/bin/env python3.5
import json
from collections import OrderedDict
from datetime import date, datetime
from functools import reduce

import jsonpath_rw
from ply import lex, yacc

__author__  = 'Simone Pandolfi <simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


DEBUG    = True
OPTIMIZE = False


DATA_TYPES = {
    'double'   : lambda: 0.0,
    'float'    : lambda: 0.0,
    'int32'    : lambda: 0,
    'int64'    : lambda: 0,
    'uint32'   : lambda: 0,
    'uint64'   : lambda: 0,
    'sint32'   : lambda: 0,
    'sint64'   : lambda: 0,
    'fixed32'  : lambda: 0,
    'fixed64'  : lambda: 0,
    'sfixed32' : lambda: 0,
    'sfixed64' : lambda: 0,
    'int'      : lambda: 0,
    'long'     : lambda: 0,
    'date'     : lambda: date.today(),
    'timestamp': lambda: datetime.now(),
    'time'     : lambda: 0,
    'bool'     : lambda: False,
    'string'   : lambda: '',
    'bytes'    : lambda: b'',
}

reserved = {
    'model'   : 'MODEL',
    'message' : 'MESSAGE',
    'enum'    : 'ENUM',
    'reserved': 'RESERVED',
    'required': 'REQUIRED',
    'optional': 'OPTIONAL',
    'repeated': 'REPEATED',
    # 'true'    : 'TRUE',
    # 'false'   : 'FALSE',
}
reserved.update({dtype: dtype.upper() for dtype in DATA_TYPES})

tokens = [
    'ASSIGN',
    'PLUS',
    'MINUS',
    'TIMES',
    'FRACT',
    'DOT',
    'COMMA',
    'SEMICOLUMN',
    'LPAREN',
    'RPAREN',
    'LINTERVAL',
    'RINTERVAL',
    'LBRACKET',
    'RBRACKET',
    'KEYWORD',
    'FLOAT_VALUE',
    'INTEGER_VALUE',
    'STRING_VALUE',
    'BOOLEAN_VALUE',
    'NAME',
] + list(reserved.values())


def find_column(token):
    """ Given the input stream which was gave to the lexer and a token,
        returns the column number of the first character.
    """
    last_cr = find_column.lexer.lexdata.rfind('\n', 0, find_column.lexer.lexpos)
    return token.lexpos - (last_cr if last_cr >= 0 else 0)


def build_lexer() -> lex.Lexer:

    t_ASSIGN         = r'='
    t_PLUS           = r'\+'
    t_MINUS          = r'\-'
    t_TIMES          = r'\*'
    t_FRACT          = r'/'
    t_DOT            = r'\.'
    t_COMMA          = r','
    t_SEMICOLUMN     = r';'
    t_LPAREN         = r'\('
    t_RPAREN         = r'\)'
    t_LINTERVAL      = r'\['
    t_RINTERVAL      = r'\]'
    t_LBRACKET       = r'\{'
    t_RBRACKET       = r'\}'
    t_STRING_VALUE   = r'".*"|\'.*\''
    t_NAME           = r'[a-zA-Z_]{1}\w*'

    def t_BOOLEAN_VALUE(t):
        r"""true|false"""
        t.value = t.value.lower() == 'true'
        return t

    def t_FLOAT_VALUE(t):
        r"""\d*\.\d+[eE]{1}[+\-]?\d*\.?\d+|\d*\.\d+"""
        t.value = float(t.value)
        return t

    def t_INTEGER_VALUE(t):
        r"""\d+"""
        t.value = int(t.value)
        return t

    def t_KEYWORD(t):
        r"""[a-zA-Z_]{1}\w*"""
        t.type = reserved.get(t.value, 'NAME')
        return t

    t_ignore         = ' \t'
    t_ignore_COMMENT = r'\#.*'  # comments will be ignored

    def t_newline(t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)

    def t_error(t):
        print("Illegal character '{0}' at {1}:{2}".format(t.value[0], t.lineno, find_column(t)))
        t.lexer.skip(1)

    lexer             = lex.lex(optimize=OPTIMIZE, debug=DEBUG)
    find_column.lexer = lexer
    return lexer


def build_parser() -> yacc.LRParser:
    lexer          = build_lexer()
    __reservations = {}

    def p_data_environment(p):
        r"""data_environment : reserved_collection object_collection
                             | reserved_collection
                             | object_collection
                             | """

        def build(reservations=set(), module={}):
            return {
                'reservations'    : reservations,
                'module'          : module,
            }

        if len(p) == 3:
            env = build(p[1], p[2])
        else:
            if isinstance(p[1], dict):
                env = build(objects=p[1])
            else:
                env = build(reservations=p[1])
        p[0] = env

    def p_object_collection(p):
        r"""object_collection : object_collection enum
                              | object_collection model
                              | object_collection message
                              | object_collection name_assignment
                              | enum
                              | model
                              | message
                              | name_assignment"""

        def get_blank():
            return {
                'objects': {},
                'vars'   : {},
            }

        def insert(collection, item):
            name                = item['name'] if isinstance(item, dict) else item[0]
            if name in reduce(lambda x, y: set(x).union(set(y)), (v.keys() for k, v in collection.items())):
                raise Exception('[object collection] Duplicated object name: {0}'.format(item['name']))
            subcollection       = collection['objects' if isinstance(item, dict) else 'vars']
            subcollection[name] = item if isinstance(item, dict) else item[1]
            return collection

        if len(p) == 3:
            collection = insert(p[1], p[2])
        else:
            collection = insert(get_blank(), p[1])
        p[0] = collection

    def p_message(p):
        r"""message : MESSAGE NAME modifier_collection LBRACKET message_definition RBRACKET"""
        p[0] = {
            'type'     : 'message',
            'name'     : p[2],
            'modifiers': p[3],
            'items'    : p[5],
        }

    def p_message_definition(p):
        r"""message_definition : message_definition enum
                               | message_definition message
                               | message_definition message_field_declaration
                               | enum
                               | message
                               | message_field_declaration
                               | """
        def get_blank():
            return {
                'objects': {},
                'fields' : {},
            }

        def insert(content, item):
            collection = 'fields' if item['type'] == 'field' else 'objects'
            if item['name'] in content[collection]:
                raise Exception('[message definition] Duplicated nested object name: {0} ({1})'.format(
                    item['name'],
                    item['type']
                ))
            content[collection][item['name']] = item
            return content

        if   len(p) == 3:
            collection = insert(p[1], p[2])
        elif len(p) == 2:
            collection = insert(get_blank(), p[1])
        else:
            collection = get_blank()
        p[0]           = collection

    def p_message_field_declaration(p):
        r"""message_field_declaration : field_multiplicity field_type NAME ASSIGN id modifier_collection SEMICOLUMN
                                      | field_multiplicity field_type NAME modifier_collection SEMICOLUMN"""
        nonlocal __reservations

        def build(multiplicity, data_type, name, modifiers, _id=None):
            if _id is not None and _id in __reservations:
                raise Exception('[message field declaration] ID was marked as reserved: {0}'.format(_id))

            return {
                'type'        : 'field',
                'multiplicity': multiplicity,
                'data_type'   : data_type,
                'name'        : name,
                'id'          : _id,
                'modifiers'   : modifiers,
            }

        p[0] = build(p[1], p[2], p[3], p[6], _id=p[5]) if len(p) == 8 else build(p[1], p[2], p[3], p[4])

    def p_model(p):
        r"""model : MODEL NAME modifier_collection LBRACKET model_definition RBRACKET"""
        p[0] = {
            'type'     : 'model',
            'name'     : p[2],
            'modifiers': p[3],
            'items'    : p[5],
        }

    def p_model_definition(p):
        r"""model_definition : model_definition enum
                             | model_definition model
                             | model_definition model_field_declaration
                             | enum
                             | model
                             | model_field_declaration
                             | """

        def get_blank():
            return {
                'objects': {},
                'fields' : {},
            }

        def insert(content, item):
            collection = 'fields' if item['type'] == 'field' else 'objects'
            if item['name'] in content[collection]:
                raise Exception('[model definition] Duplicated nested object name: {0} ({1})'.format(
                    item['name'],
                    item['type']
                ))
            content[collection][item['name']] = item
            return content

        if   len(p) == 3:
            collection = insert(p[1], p[2])
        elif len(p) == 2:
            collection = insert(get_blank(), p[1])
        else:
            collection = get_blank()
        p[0]           = collection
    
    def p_model_field_declaration(p):
        r"""model_field_declaration : field_multiplicity field_type NAME ASSIGN id modifier_collection SEMICOLUMN"""
        nonlocal __reservations

        _id = p[5]
        if _id in __reservations:
            raise Exception('[model field declaration] ID was marked as reserved: {0}'.format(_id))

        p[0] = {
            'type'        : 'field',
            'multiplicity': p[1],
            'data_type'   : p[2],
            'name'        : p[3],
            'id'          : _id,
            'modifiers'   : p[6],
        }

    def p_field_multiplicity(p):
        r"""field_multiplicity : REQUIRED
                               | OPTIONAL
                               | REPEATED"""
        p[0] = p[1]

    def p_field_type(p):
        r"""field_type : DOUBLE
                       | FLOAT
                       | INT32
                       | INT64
                       | UINT32
                       | UINT64
                       | SINT32
                       | SINT64
                       | FIXED32
                       | FIXED64
                       | SFIXED32
                       | SFIXED64
                       | INT
                       | LONG
                       | DATE
                       | TIMESTAMP
                       | TIME
                       | BOOL
                       | STRING
                       | BYTES
                       | nested_value"""
        p[0] = p[1]

    def p_modifier_collection(p):
        r"""modifier_collection : modifier_collection LINTERVAL name_assignment RINTERVAL
                                | modifier_collection LINTERVAL NAME RINTERVAL
                                | LINTERVAL name_assignment RINTERVAL
                                | LINTERVAL NAME RINTERVAL
                                | """

        def key_value(aux):
            if isinstance(aux, tuple):
                return aux    # name_assignment
            return aux, True  # nested_value

        if len(p) == 5:
            key, value          = key_value(p[3])
            collection          = p[1]
            if key in collection:
                raise Exception('[modifier collection] Duplicated key: {0}'.format(key))
            collection[key]     = value
        else:
            collection          = {}
            if len(p) == 4:
                key, value      = key_value(p[2])
                collection[key] = value
        p[0]                    = collection

    def p_enum(p):
        r"""enum : ENUM NAME LBRACKET enum_definition RBRACKET"""
        p[0] = {
            'type' : 'enum',
            'name' : p[2],
            'items': p[4],
        }

    def p_enum_definition(p):
        r"""enum_definition : enum_definition COMMA name_assignment
                            | enum_definition COMMA NAME
                            | name_assignment
                            | NAME"""

        def add(collection, aux):
            # if aux is an instance of a tuple, than it means that the parser recognized it as a 'name_assignment',
            # otherwise is has been intended as a 'NAME'
            key, value = aux if isinstance(aux, tuple) else aux, len(collection)
            if key in collection:
                raise Exception('[enum definition] Duplicated key: {0}'.format(key))
            collection[key] = value
            return collection

        p[0] = add(p[1], p[3]) if len(p) == 4 else add(OrderedDict(), p[1])

    def p_reserved_collection(p):
        r"""reserved_collection : reserved_collection RESERVED LINTERVAL id COMMA id RINTERVAL SEMICOLUMN
                                | reserved_collection RESERVED id_collection SEMICOLUMN
                                | RESERVED LINTERVAL id COMMA id RINTERVAL SEMICOLUMN
                                | RESERVED id_collection SEMICOLUMN"""
        nonlocal __reservations

        def add(collection, ids):
            ids = ids if isinstance(ids, set) else {_id for _id in ids}
            intersection = collection.intersection(ids)
            if any(intersection):
                raise Exception('[reservation] Duplicated ID: {0}'.format(', '.join(str(_id) for _id in intersection)))
            collection.update(ids)
            return collection

        if   len(p) == 9:
            collection = add(p[1], range(p[4], p[6] + 1))
        elif len(p) == 8:
            collection = add(set(), range(p[3], p[5] + 1))
        elif len(p) == 5:
            collection = add(p[1], p[3])
        else:
            collection = add(set(), p[2])
        __reservations = collection
        p[0]           = collection

    def p_name_assignment(p):
        r"""name_assignment : NAME ASSIGN STRING_VALUE
                            | NAME ASSIGN FLOAT_VALUE
                            | NAME ASSIGN INTEGER_VALUE
                            | NAME ASSIGN BOOLEAN_VALUE
                            | NAME ASSIGN nested_value"""
        p[0] = (p[1], p[3])

    def p_nested_value(p):
        r"""nested_value : nested_value DOT NAME
                         | NAME"""
        p[0] = len(p) == 4 and p[1] + [p[3]] or [p[1]]

    def p_id_collection(p):
        r"""id_collection : id_collection COMMA id
                          | id"""

        def add(collection, _id):
            if _id in collection:
                raise Exception('[ID collection] Duplicated ID: {0}'.format(_id))
            collection.add(_id)
            return collection

        p[0] = add(p[1], p[3]) if len(p) == 4 else add(set(), p[1])

    def p_id(p):
        r"""id : INTEGER_VALUE"""
        p[0] = p[1]

    def p_error(p):
        print('Syntax error!', p)

    return yacc.yacc(optimize=OPTIMIZE, debug=DEBUG)


def parse(_input):
    if not isinstance(_input, str) and not (hasattr(_input, 'read') and callable(_input.read)):
        raise TypeError("Expected input was string or a character input stream, got '{0}'".format(
            type(_input).__name__)
        )

    if not isinstance(_input, str):
        _input = _input.read()

    return build_parser().parse(_input)


def build(config):
    if not isinstance(config, (str, ConfigStruct)):
        raise TypeError('Expected config was a string or a ConfigStruct, got: {}'.format(type(config).__name__))

    if isinstance(config, str):
        config = ConfigStruct(config)

    environment = {
        'reservations': {},
        'modules'     : [],
    }

    obj_names   = {}  # set of all objects names defined at root level
    dobj_names  = {}  # set of all duplicated objects names defined at root level

    for modulename in config.modules:
        module       = parse(modulename)

        # merges the IDs set
        intersection = module['reservations'].intersection(environment['reservations'])
        if any(intersection):
            raise Exception("Duplicated object names: {0}".format(', '.join(intersection)))
        environment['reservations'].update(module['reservations'])

        # merges the modules
        names        = set(module['module']['objects'].keys())
        intersection = names.intersection(obj_names)
        obj_names.update(names)
        dobj_names.update(intersection)
        environment['modules'].append(module['module'])

    # TODO validare gli ID
    # TODO creare il grafo ed i reverse reference


class ConfigStruct:
    __slots__ = ('__modules',)

    def __init__(self, config_filepath):
        if not isinstance(config_filepath, str):
            raise TypeError("Expected 'conf' was a string, got: {0}".format(type(config_filepath).__name__))

        with open(config_filepath, 'r') as fp:
            buff = json.load(fp)

        self.__modules = [match.value for match in jsonpath_rw.parse('modules[*]').find(buff)]

    @property
    def modules(self) -> iter:
        return iter(self.__modules)

"""

{
    "modules": []
}

"""


if __name__ == '__main__':

    from pprint import PrettyPrinter
    PP = PrettyPrinter(indent=True)

    # with open('test1.promap') as fp:
    #     PP.pprint(parse(fp))

    config = ConfigStruct('test_config.json')
    PP.pprint(config.modules)
