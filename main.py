#!/usr/bin/env python3.5
import importlib
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import date, datetime
from functools import reduce
from itertools import chain

import jsonpath_rw
from cerberus import Validator
from ply import lex, yacc

__author__  = 'Simone Pandolfi'
__email__   = '<simopandolfi@gmail.com>'
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
    'string'   : lambda: '""',
    'bytes'    : lambda: b'',
}

KINDS = ('required', 'optional', 'repeated')

reserved = {
    'model'   : 'MODEL',
    'message' : 'MESSAGE',
    'enum'    : 'ENUM',
    'reserved': 'RESERVED',
    #'required': 'REQUIRED',
    #'optional': 'OPTIONAL',
    #'repeated': 'REPEATED',
    'alias'   : 'ALIAS',
    'void'    : 'VOID',
    # 'true'    : 'TRUE',
    # 'false'   : 'FALSE',
    'resource': 'RESOURCE',
    'service' : 'SERVICE',
}
reserved.update({dtype: dtype.upper() for dtype in DATA_TYPES})
reserved.update({kind: kind.upper() for kind in KINDS})

tokens = [
    'ASSIGN',
    'PLUS',
    'MINUS',
    'TIMES',
    'FRACT',
    'DOT',
    'COMMA',
    'COLON',
    'SEMICOLUMN',
    'LPAREN',
    'RPAREN',
    'LINTERVAL',
    'RINTERVAL',
    'LBRACKET',
    'RBRACKET',
    'AT',
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


def make_model_field(multiplicity, datatype, name, _id, modifiers={}, source_field=None):
    def check_type(label: str, var, _type):
        if not isinstance(var, _type):
            raise TypeError("{0} must be a {1}, got: {2}".format(label.title(), _type.__name__, type(var).__name__))

    check_type('multiplicity', multiplicity, str)
    check_type('name', name, str)
    check_type('_id', _id, int)
    check_type('modifiers', modifiers, dict)

    if not isinstance(datatype, (str, list, dict)):
        raise TypeError("Datatype must be a string, a list or a dict; got: {0}".format(type(datatype).__name__))

    if not isinstance(source_field, dict) and source_field is not None:
        raise TypeError("Source filed must be a dict or None; got: {0}".format(type(source_field).__name__))

    return {
        'type'        : 'field',
        'multiplicity': multiplicity,
        'data_type'   : datatype,
        'name'        : name,
        'id'          : _id,
        'modifiers'   : modifiers,
        'source_field': source_field,
    }


def make_model(name, modifiers={}, fields={}, objects={}):
    return {
        'type'     : 'model',
        'name'     : name,
        'fullname' : [name],
        'modifiers': modifiers,
        'fields'   : fields,
        'objects'  : objects,
    }


def build_lexer() -> lex.Lexer:

    t_ASSIGN         = r'='
    t_PLUS           = r'\+'
    t_MINUS          = r'\-'
    t_TIMES          = r'\*'
    t_FRACT          = r'/'
    t_DOT            = r'\.'
    t_COMMA          = r','
    t_COLON          = r':'
    t_SEMICOLUMN     = r';'
    t_LPAREN         = r'\('
    t_RPAREN         = r'\)'
    t_LINTERVAL      = r'\['
    t_RINTERVAL      = r'\]'
    t_LBRACKET       = r'\{'
    t_RBRACKET       = r'\}'
    t_AT             = r'@'
    t_STRING_VALUE   = r'".*?"|\'.*?\''
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

    # def t_TIMESTAMP(t):  # TODO implementare le conversioni per timestamp, date e time (usando il formato ISO)
    #     r""""""

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

    def p_schema(p):
        r"""schema : schema reservation
                   | schema enum
                   | schema model
                   | schema message
                   | schema resource
                   | schema service
                   | schema variable
                   | schema alias
                   | reservation
                   | enum
                   | model
                   | message
                   | resource
                   | service
                   | variable
                   | alias"""

        def add(arg, schema=Schema()):
            schema.add(arg)
            return schema

        if len(p) == 3:
            p[0] = add(p[2], schema=p[1])
        else:
            p[0] = add(p[1])

    def p_reservation(p):
        r"""reservation : RESERVED LINTERVAL id COMMA id RINTERVAL
                        | RESERVED id_array"""
        if len(p) == 7:
            p[0] = Reservation(*[_id for _id in range(p[3], p[5] + 1)])
        else:
            p[0] = Reservation(*p[2])

    def p_id_array(p):
        r"""id_array : id_array COMMA id
                     | id"""
        if len(p) == 4:
            p[1].add(p[3])
            p[0] = p[1]
        else:
            p[0] = {p[1]}

    def p_variable(p):
        r"""variable : NAME ASSIGN datatype
                     | NAME ASSIGN full_qualified_name"""
        p[0] = Variable(p[1], p[3])

    def p_alias(p):
        r"""alias : ALIAS NAME full_qualified_name"""
        p[0] = Alias(p[2], p[3])

    def p_enum(p):
        r"""enum : ENUM NAME LBRACKET enum_content RBRACKET"""
        p[0] = Enum(p[2], choices=p[4])

    def p_enum_content(p):
        r"""enum_content : enum_content COMMA NAME ASSIGN basetype
                         | enum_content COMMA NAME
                         | NAME ASSIGN basetype
                         | NAME"""

        def add(key, value=None, collection=OrderedDict()):
            if key in collection:
                raise DuplicatedEnumChoiceException('Duplicated enum choice: {0}'.format(key))
            collection[key] = value
            return collection

        if len(p) == 6:
            p[0] = add(p[3], value=p[5], collection=p[1])
        elif len(p) == 4:
            if isinstance(p[1], dict):
                p[0] = add(p[3], collection=p[1])
            else:
                p[0] = add(p[1], value=p[3])
        else:
            p[0] = add(p[1])

    def p_model(p):
        r"""model : annotation_array MODEL NAME modifier_array LBRACKET model_content RBRACKET"""
        gen_annotations = ((k, v) for k, v in p[1].items())
        gen_modifiers   = ((k, v) for k, v in p[4].items())
        gen_models      = (x for x in p[6] if isinstance(x, Model))
        gen_enums       = (x for x in p[6] if isinstance(x, Enum))
        gen_fields      = (x for x in p[6] if isinstance(x, Field))
        p[0] = Model(p[3], modifiers=chain(gen_annotations, gen_modifiers), models=gen_models, enums=gen_enums, fields=gen_fields)

    def p_model_content(p):
        r"""model_content : model_content model
                          | model_content enum
                          | model_content model_field
                          | model
                          | enum
                          | model_field"""
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_model_field(p):
        r"""model_field : annotation_array REQUIRED full_qualified_name NAME ASSIGN id modifier_array
                        | annotation_array OPTIONAL full_qualified_name NAME ASSIGN id modifier_array
                        | annotation_array REPEATED full_qualified_name NAME ASSIGN id modifier_array
                        | annotation_array REQUIRED basetype NAME ASSIGN id modifier_array
                        | annotation_array OPTIONAL basetype NAME ASSIGN id modifier_array
                        | annotation_array REPEATED basetype NAME ASSIGN id modifier_array"""
        annotation_gen = ((k, v) for k, v in p[1].items())
        modifiers_gen  = ((k, v) for k, v in p[7].items())
        p[0] = Field(p[4], p[6], p[3], p[2], modifiers=chain(annotation_gen, modifiers_gen))

    def p_message(p):
        r"""message : annotation_array MESSAGE NAME modifier_array LBRACKET message_content RBRACKET"""
        gen_annotations = ((k, v) for k, v in p[1].items())
        gen_modifiers   = ((k, v) for k, v in p[4].items())
        gen_messages    = (x for x in p[6] if isinstance(x, Message))
        gen_enums       = (x for x in p[6] if isinstance(x, Enum))
        gen_fields      = (x for x in p[6] if isinstance(x, Field))
        p[0] = Message(p[3], modifiers=chain(gen_annotations, gen_modifiers), messages=gen_messages, enum=gen_enums, fields=gen_fields)

    def p_message_content(p):
        r"""message_content : message_content message
                            | message_content enum
                            | message_content message_field
                            | message
                            | enum
                            | message_field"""
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_message_field(p):
        r"""message_field : annotation_array REQUIRED full_qualified_name NAME ASSIGN id modifier_array
                          | annotation_array OPTIONAL full_qualified_name NAME ASSIGN id modifier_array
                          | annotation_array REPEATED full_qualified_name NAME ASSIGN id modifier_array
                          | annotation_array REQUIRED basetype NAME ASSIGN id modifier_array
                          | annotation_array OPTIONAL basetype NAME ASSIGN id modifier_array
                          | annotation_array REPEATED basetype NAME ASSIGN id modifier_array
                          | annotation_array REQUIRED full_qualified_name NAME modifier_array
                          | annotation_array OPTIONAL full_qualified_name NAME modifier_array
                          | annotation_array REPEATED full_qualified_name NAME modifier_array
                          | annotation_array REQUIRED basetype NAME modifier_array
                          | annotation_array OPTIONAL basetype NAME modifier_array
                          | annotation_array REPEATED basetype NAME modifier_array"""
        annotation_gen = ((k, v) for k, v in p[1].items())
        if len(p) == 8:
            modifiers_gen = ((k, v) for k, v in p[7].items())
            _id           = p[6]
        else:
            modifiers_gen = ((k, v) for k, v in p[5].items())
            _id           = None
        p[0] = Field(p[4], _id, p[3], p[2], modifiers=chain(annotation_gen, modifiers_gen))

    def p_resource(p):
        r"""resource : annotation_array RESOURCE NAME modifier_array LBRACKET resource_content RBRACKET"""
        gen_annotations = ((k, v) for k, v in p[1].items())
        gen_modifiers   = ((k, v) for k, v in p[4].items())
        p[0] = Resource(p[3], endpoints=p[6], modifiers=chain(gen_annotations, gen_modifiers))

    def p_resource_content(p):
        r"""resource_content : resource_content endpoint
                             | endpoint"""
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_endpoint(p):
        r"""endpoint : annotation_array NAME LPAREN full_qualified_name RPAREN COLON full_qualified_name modifier_array
                     | annotation_array NAME LPAREN full_qualified_name RPAREN COLON basetype modifier_array
                     | annotation_array NAME LPAREN full_qualified_name RPAREN COLON VOID modifier_array
                     | annotation_array NAME LPAREN basetype RPAREN COLON full_qualified_name modifier_array
                     | annotation_array NAME LPAREN basetype RPAREN COLON basetype modifier_array
                     | annotation_array NAME LPAREN basetype RPAREN COLON VOID modifier_array
                     | annotation_array NAME LPAREN RPAREN COLON full_qualified_name modifier_array
                     | annotation_array NAME LPAREN RPAREN COLON basetype modifier_array
                     | annotation_array NAME LPAREN RPAREN COLON VOID modifier_array"""
        gen_annotations = ((k, v) for k, v in p[1].items())
        if len(p) == 9:
            gen_modifiers = ((k, v) for k, v in p[8].items())
            payload       = p[4]
            response      = p[7]
        else:
            gen_modifiers = ((k, v) for k, v in p[7].items())
            payload       = 'void'
            response      = p[6]
        p[0] = Endpoint(p[2], payload, response, modifiers=chain(gen_annotations, gen_modifiers))

    def p_service(p):
        r"""service : annotation_array SERVICE NAME modifier_array LBRACKET service_content RBRACKET"""
        gen_annotations = ((k ,v) for k, v in p[1].items())
        gen_modifiers   = ((k ,v) for k, v in p[4].items())
        p[0] = Service(p[3], methods=p[6], modifiers=chain(gen_annotations, gen_modifiers))

    def p_service_content(p):
        r"""service_content : service_content service_method
                            | service_method"""
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_service_method(p):
        r"""service_method : annotation_array NAME LPAREN service_method_args RPAREN COLON full_qualified_name modifier_array
                           | annotation_array NAME LPAREN service_method_args RPAREN COLON basetype modifier_array
                           | annotation_array NAME LPAREN service_method_args RPAREN COLON VOID modifier_array
                           | annotation_array NAME LPAREN RPAREN COLON full_qualified_name modifier_array
                           | annotation_array NAME LPAREN RPAREN COLON basetype modifier_array
                           | annotation_array NAME LPAREN RPAREN COLON VOID modifier_array"""
        gen_annotations = ((k, v) for k, v in p[1].items())
        if len(p) == 9:
            attrs         = p[4]
            outattr       = p[7]
            gen_modifiers = ((k, v) for k, v in p[8].items())
        else:
            attrs         = 'void'
            outattr       = p[6]
            gen_modifiers = ((k, v) for k, v in p[7].items())
        p[0] = ServiceMethod(p[2], attrs=attrs, response=outattr, modifiers=chain(gen_annotations, gen_modifiers))

    def p_service_method_args(p):
        r"""service_method_args : service_method_args COMMA full_qualified_name NAME
                                | service_method_args COMMA basetype NAME
                                | full_qualified_name NAME
                                | basetype NAME"""
        if len(p) == 5:
            p[1].append((p[4], p[3]))
            p[0] = p[1]
        else:
            p[0] = [(p[2], p[1])]

    def p_modifier_array(p):
        r"""modifier_array : modifier_array LINTERVAL NAME ASSIGN basetypevalue RINTERVAL
                           | modifier_array LINTERVAL NAME ASSIGN full_qualified_name RINTERVAL
                           | modifier_array LINTERVAL NAME RINTERVAL
                           | LINTERVAL NAME ASSIGN basetypevalue RINTERVAL
                           | LINTERVAL NAME ASSIGN full_qualified_name RINTERVAL
                           | LINTERVAL NAME RINTERVAL
                           | """

        def add(key, value=True, collection=OrderedDict()):
            if key in collection:
                raise DuplicatedVariableException('Duplicated modifier: {0}'.format(key))
            collection[key] = value
            return collection

        if len(p) == 7:
            p[0] = add(p[3], value=p[5], collection=p[1])
        elif len(p) == 5:
            p[0] = add(p[3], collection=p[1])
        elif len(p) == 6:
            p[0] = add(p[2], value=p[4])
        elif len(p) == 4:
            p[0] = add(p[2])
        else:
            p[0] = OrderedDict()

    def p_annotation_array(p):
        r"""annotation_array : annotation_array AT NAME LPAREN basetypevalue RPAREN
                             | annotation_array AT NAME LPAREN full_qualified_name RPAREN
                             | annotation_array AT NAME
                             | AT NAME LPAREN basetypevalue RPAREN
                             | AT NAME LPAREN full_qualified_name RPAREN
                             | AT NAME
                             | """

        def add(key, value=True, collection=OrderedDict()):
            if key in collection:
                raise DuplicatedVariableException('Duplicated annotation: {0}'.format(key))
            collection[key] = value
            return collection

        if len(p) == 7:
            p[0] = add(p[3], value=p[5], collection=p[1])
        elif len(p) == 4:
            p[0] = add(p[3], collection=p[1])
        elif len(p) == 6:
            p[0] = add(p[2], value=p[4])
        elif len(p) == 3:
            p[0] = add(p[2])
        else:
            p[0] = OrderedDict()

    def p_map(p):
        r"""map : LBRACKET map_content RBRACKET"""
        p[0] = Map(**p[2])

    def p_map_content(p):
        r"""map_content : map_content COMMA NAME COLON basetypevalue
                        | map_content COMMA NAME COLON full_qualified_name
                        | map_content COMMA basetypevalue COLON basetypevalue
                        | NAME COLON basetypevalue
                        | NAME COLON full_qualified_name
                        | basetypevalue COLON basetypevalue"""

        def add(key, value, collection=OrderedDict()):
            if key in collection:
                raise DuplicatedVariableException('Duplicated map key: {0}'.format(key))
            collection[key] = value
            return collection

        if len(p) == 6:
            p[0] = add(p[3], p[5], collection=p[1])
        else:
            p[0] = add(p[1], p[3])

    def p_datatype(p):
        r"""datatype : map
                     | array
                     | basetypevalue"""
        p[0] = p[1]

    def p_array(p):
        r"""array : LINTERVAL array_content RINTERVAL"""
        p[0] = Array(*p[2])

    def p_array_content(p):
        r"""array_content : array_content COMMA datatype
                          | array_content COMMA full_qualified_name
                          | basetypevalue
                          | full_qualified_name"""

        def add(value, collection=[]):
            collection.append(value)
            return collection

        if len(p) == 4:
            p[0] = add(p[3], collection=p[1])
        else:
            p[0] = add(p[1])

    def p_basetype(p):
        r"""basetype : DOUBLE
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
                     | BYTES"""
        p[0] = p[1]

    def p_basetypevalue(p):
        r"""basetypevalue : FLOAT_VALUE
                          | INTEGER_VALUE
                          | BOOLEAN_VALUE
                          | STRING_VALUE"""
        p[0] = p[1]

    def p_full_qualified_name(p):
        r"""full_qualified_name : full_qualified_name DOT NAME
                                | NAME"""
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_id(p):
        r"""id : INTEGER_VALUE"""
        p[0] = p[1]

    def p_error(p):
        print('Syntax error!', p)

    return yacc.yacc(optimize=OPTIMIZE, debug=DEBUG)


def build(modules: list, buildername: str, params=[]):
    schema = Schema()
    for module in modules:
        schema.merge(module)

    schema.build_model_graph(modelcontainer=schema)
    schema.build_message_graph(messagecontainer=schema)
    schema.validate_services()
    schema.validate_resources()

    # makes
    builder = importlib.import_module('builders.{0}'.format(buildername))
    if not hasattr(builder, 'build') or not callable(builder.build):
        raise NameError("Missing 'build' function in builder: {0}".format(buildername))
    builder.build(schema, **params)


class UnknownDataTypeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class EndpointValidationException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class DuplicatedModifierException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedFieldException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedEnumChoiceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedEnumException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedModelException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedMessageException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedEndpointException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedServiceMethodException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedVariableException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedAliasException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedResourceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedServiceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedReservationException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DuplicatedArgumentNameException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class ReservedIdInUseException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class IdAlreadyInUseException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DataStructNotFoundException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class ModelNotFoundException(DataStructNotFoundException):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class MessageNotFoundException(DataStructNotFoundException):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class UnknownFieldMappingException(DataStructNotFoundException):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class DataTypeMismatchException(DataStructNotFoundException):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class FieldException(DataStructNotFoundException):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class ConfigStruct:
    __slots__ = ('__builds', '__parser', '__modules')

    def __init__(self, config_filepath):
        if not isinstance(config_filepath, str):
            raise TypeError("Expected 'conf' was a string, got: {0}".format(type(config_filepath).__name__))
        with open(config_filepath, 'r') as fp:
            buff = json.load(fp)
        self.__builds  = {
            builddef['builder']: builddef
                for builddef in [
                    ConfigStruct.__validate_build(builddef.value)
                        for builddef in jsonpath_rw.parse('builds[*]').find(buff)
                ]
        }
        self.__parser  = build_parser()
        self.__modules = {}

    @staticmethod
    def __validate_build(builddef):
        confdef = {
            'builder': {'type': 'string'},
            'params' : {'type': 'dict', 'keyschema': {'type': 'string'}},
            'enabled': {'type': 'boolean'},
            'modules': {'type': 'list', 'schema': {'type': 'string'}},
        }

        validator = Validator(confdef)
        if not validator.validate(builddef):
            raise SyntaxError("Invalid build definition: {0}".format(builddef))
        return builddef

    @property
    def builds(self):
        return (buildname for buildname in self.__builds)

    def __parse(self, modulepath):
        if modulepath in self.__modules:
            return self.modules[modulepath]
        with open(modulepath, 'r') as fp:
            buff = fp.read()
        module = self.__parser.parse(buff)
        self.__modules[modulepath] = module
        return module

    def build(self):
        for buildername in self.builds:
            buildattrs = self.__builds.get(buildername, None)
            if buildattrs is not None and buildattrs.get('enabled', False) is True:
                modules = set(self.__parse(modulepath) for modulepath in buildattrs['modules'])
                build(modules, buildername, params=self.__builds[buildername]['params'])


class Map(OrderedDict):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)


class Array(list):
    def __init__(self, *args):
        super().__init__(self, args)


class Field:
    __slots__ = ('__kind', '__datatype', '__name', '__id', 'modifiers', 'parent', '__mapped_model_field')

    def __init__(self, name, id, datatype, kind, modifiers=None, parent=None):
        self.__name               = name
        self.__id                 = id
        self.__datatype           = datatype
        self.__kind               = kind
        self.modifiers            = OrderedDict()
        self.parent               = parent
        self.__mapped_model_field = None

        if modifiers is not None:
            for k, v in modifiers:
                if k in self.modifiers:
                    raise DuplicatedVariableException('Duplicated modifiers: {0}'.format(k))
                self.modifiers[k] = v

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id

    @property
    def datatype(self):
        return self.__datatype

    @datatype.setter
    def datatype(self, datatype):
        self.__datatype = datatype

    @property
    def kind(self):
        return self.__kind

    @property
    def fullname(self):
        return '.'.join(self.get_fullname())

    @property
    def model_field(self):
        if isinstance(self.parent, Message):
            return self.__mapped_model_field
        return None

    @model_field.setter
    def model_field(self, field):
        if isinstance(self.parent, Message) and isinstance(field.parent, Model):
            self.__mapped_model_field = field

    def get_fullname(self):
        name = [self.name]
        parent = self.parent
        while parent is not None:
            name.insert(0, parent.name)
            parent = parent.parent
        return name

    def add_modifier(self, key, value=True):
        if key in self.modifiers:
            raise DuplicatedModifierException('Duplicated modifier name: {0}'.format(key))
        self.modifiers[key] = value


class Reservation(set):
    def __init__(self, *args):
        super().__init__(self, args)


class Enum:
    __slots__ = ('__name', 'choices', 'parent')

    def __init__(self, name, choices=None, parent=None):
        self.__name  = name
        self.choices = OrderedDict()
        self.parent  = parent

        if choices is not None:
            for k, v in choices.items():
                self.add_choice(k, v)

    @property
    def name(self):
        return self.__name

    def add_choice(self, key, value=None):
        if key in self.choices:
            raise DuplicatedEnumChoiceException('Duplicated choice name: {0}'.format(key))
        self.choices[key] = value if value is not None else len(self.choices)


class Model:
    __slots__ = ('__name', 'modifiers', 'fields', 'models', 'enums', 'parent')

    def __init__(self, name, modifiers=None, fields=None, models=None, enums=None, parent=None):
        # TODO maybe would be a great idea if the arguments will be validated before assignment
        self.__name    = name
        self.modifiers = OrderedDict()
        self.fields    = OrderedDict()
        self.models    = OrderedDict()
        self.enums     = OrderedDict()
        self.parent    = None

        self.__load(modifiers, addfunc=self.add_modifier)
        self.__load(fields, addfunc=self.add_field)
        self.__load(models, addfunc=self.add_model)
        self.__load(enums, addfunc=self.add_enum)

    @staticmethod
    def __load(args, addfunc):
        if args is not None:
            for arg in args:
                addfunc(arg)

    @property
    def name(self):
        return self.__name

    @property
    def fullname(self):
        return '.'.join(self.get_fullname())

    def get_fullname(self):
        name   = [self.name]
        parent = self.parent
        while parent is not None:
            name.insert(0, parent.name)
            parent = parent.parent
        return name

    def add_modifier(self, key, value=True):
        if isinstance(key, tuple) and len(key) == 2:
            value = key[1]
            key   = key[0]
        if key in self.modifiers:
            raise DuplicatedModifierException('Duplicated modifier name: {0}'.format(key))
        self.modifiers[key] = value

    def add_field(self, field: Field) -> None:
        if field.name in self.fields:
            raise DuplicatedFieldException('Duplicated field name: {0}'.format(field.name))
        field.parent = self
        self.fields[field.name] = field

    def add_model(self, model: 'Model') -> None:
        if model.name in self.models:
            raise DuplicatedModelException('Duplicated model name: {0}'.format(model.name))
        model.parent = self
        self.models[model.name] = model

    def add_enum(self, enum: Enum) -> None:
        if enum.name in self.enums:
            raise DuplicatedEnumException('Duplicated enum name: {0}'.format(enum.name))
        enum.parent = self
        self.enums[enum.name] = enum

    def visit_models(self, parentbefore=False):
        for model in self.models.values():
            if parentbefore:
                yield model
                yield from model.visit_models(parentbefore=parentbefore)
            else:
                yield from model.visit_models(parentbefore=parentbefore)
                yield model


class Message:
    __slots__ = ('__name', 'modifiers', 'fields', 'messages', 'enums', 'parent')

    def __init__(self, name, modifiers=None, fields=None, messages=None, enums=None, parent=None):
        # TODO maybe would be a great idea if the arguments will be validated before assignment
        self.__name    = name
        self.modifiers = OrderedDict()
        self.fields    = OrderedDict()
        self.messages  = OrderedDict()
        self.enums     = OrderedDict()
        self.parent    = None

        self.__load(modifiers, addfunc=self.add_modifier)
        self.__load(fields, addfunc=self.add_field)
        self.__load(messages, addfunc=self.add_message)
        self.__load(enums, addfunc=self.add_enum)

    @staticmethod
    def __load(args, addfunc):
        if args is not None:
            for arg in args:
                addfunc(arg)

    @property
    def name(self):
        return self.__name

    @property
    def fullname(self):
        return '.'.join(self.get_fullname())

    def get_fullname(self):
        name = [self.name]
        parent = self.parent
        while parent is not None:
            name.insert(0, parent.name)
            parent = parent.parent
        return name

    def add_modifier(self, key, value=True):
        if key in self.modifiers:
            raise DuplicatedModifierException('Duplicated modifier name: {0}'.format(key))
        self.modifiers[key] = value

    def add_field(self, field: Field) -> None:
        if field.name in self.fields:
            raise DuplicatedFieldException('Duplicated field name: {0}'.format(field.name))
        self.parent = self
        self.fields[field.name] = field

    def add_message(self, message: 'Message') -> None:
        if message.name in self.messages:
            raise DuplicatedMessageException('Duplicated message name: {0}'.format(message.name))
        self.parent = self
        self.messages[message.name] = message

    def add_enum(self, enum: Enum) -> None:
        if enum.name in self.enums:
            raise DuplicatedEnumException('Duplicated enum name: {0}'.format(enum.name))
        self.parent = self
        self.enums[enum.name] = enum


class Endpoint:
    __slots__ = ('__name', 'payload', 'response', 'modifiers', 'resource')

    def __init__(self, name, payload, response, modifiers=None, resource=None):
        self.__name     = name
        self.payload  = payload
        self.response = response
        self.modifiers  = OrderedDict()
        self.resource   = resource

        if modifiers is not None:
            for k, v in modifiers:
                if k in self.modifiers:
                    raise DuplicatedVariableException('Duplicated modifiers: {0}'.format(k))
                self.modifiers[k] = v

    @property
    def name(self):
        return self.__name

    def add_modifier(self, key, value=True):
        if key in self.modifiers:
            raise DuplicatedModifierException('Duplicated modifier name: {0}'.format(key))
        self.modifiers[key] = value

    def __str__(self):
        return '{0}.{1}'.format(self.resource.name, self.name)


class Resource:
    __slots__ = ('__name', 'modifiers', 'endpoints')

    def __init__(self, name, endpoints=None, modifiers=None):
        self.__name    = name
        self.modifiers = OrderedDict()
        self.endpoints = OrderedDict()

        if modifiers is not None:
            for k, v in modifiers:
                if k in self.modifiers:
                    raise DuplicatedVariableException('Duplicated modifiers: {0}'.format(k))
                self.modifiers[k] = v

        if endpoints is not None:
            for endpoint in endpoints:
                if endpoint.name in self.endpoints:
                    raise DuplicatedEndpointException('Duplicated endpoint: {0}'.format(endpoint.name))
                self.add_endpoint(endpoint)

    @property
    def name(self):
        return self.__name

    def add_modifier(self, key, value=True):
        if key in self.modifiers:
            raise DuplicatedModifierException('Duplicated modifier name: {0}'.format(key))
        self.modifiers[key] = value

    def add_endpoint(self, endpoint: Endpoint):
        if endpoint.name in self.endpoints:
            raise DuplicatedEndpointException('Duplicated endpoint name: {0}'.format(endpoint.name))
        endpoint.resource = self
        self.endpoints[endpoint.name] = endpoint


class ServiceMethod:
    __slots__ = ('__name', 'attrs', 'response', 'modifiers', 'service')

    def __init__(self, name, attrs=None, response=None, modifiers=None, service=None):
        self.__name    = name
        self.attrs     = OrderedDict()
        self.response  = response
        self.modifiers = OrderedDict()
        self.service   = service

        for k, v in attrs.items():
            if k in self.attrs:
                raise DuplicatedArgumentNameException('Duplicated argument name: {0}'.format(k))
            self.attrs[k] = v

        if modifiers is not None:
            for k, v in modifiers:
                if k in self.modifiers:
                    raise DuplicatedVariableException('Duplicated modifiers: {0}'.format(k))
                self.modifiers[k] = v

    @property
    def name(self):
        return self.__name

    def add_modifier(self, key, value=True):
        if key in self.modifiers:
            raise DuplicatedModifierException(
                'Duplicated modifier name: {0}'.format(key))
        self.modifiers[key] = value


class Service:
    __slots__ = ('__name', 'methods', 'modifiers')

    def __init__(self, name, methods=None, modifiers=None):
        self.__name    = name
        self.methods   = OrderedDict()
        self.modifiers = OrderedDict()

        if modifiers is not None:
            for k, v in modifiers:
                if k in self.modifiers:
                    raise DuplicatedVariableException('Duplicated modifiers: {0}'.format(k))
                self.modifiers[k] = v

        if methods is not None:
            for method in methods:
                if method.name in self.methods:
                    raise DuplicatedServiceMethodException('Duplicated service method: {0}'.format(method.name))
                self.methods[method.name] = method

    @property
    def name(self):
        return self.__name

    def add_modifier(self, key, value=True):
        if key in self.modifiers:
            raise DuplicatedModifierException('Duplicated modifier name: {0}'.format(key))
        self.modifiers[key] = value

    def add_method(self, method):
        if method.name in self.methods:
            raise DuplicatedServiceMethodException('Duplicated service method name: {0}'.format(method.name))
        method.service = self
        self.methods[method.name] = method


class Variable:
    __slots__ = ('__name', '__value')

    def __init__(self, name, value):
        self.__name  = name
        self.__value = value

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value


class Alias:
    __slots__ = ('__name', '__value')

    def __init__(self, name, value):
        self.__name  = name
        self.__value = value

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value


class Schema:
    __slots__ = ('__variables', '__aliases', '__models', '__messages', '__resources', '__services', '__reservations', '__mapped_fields')

    def __init__(self, variables=[], aliases=[], models=[], messages=[], resources=[], services=[], reservations=set()):
        self.__variables     = OrderedDict()
        self.__aliases       = OrderedDict()
        self.__models        = OrderedDict()
        self.__messages      = OrderedDict()
        self.__resources     = OrderedDict()
        self.__services      = OrderedDict()
        self.__reservations  = set()
        self.__mapped_fields = {}

        for arg in chain(variables, aliases, models, messages, resources, services, reservations):
            self.add(arg)

    def __collections(self):
        return {
            Variable   : self.__variables,
            Alias      : self.__aliases,
            Model      : self.__models,
            Message    : self.__messages,
            Resource   : self.__resources,
            Service    : self.__services,
            Reservation: self.__reservations,
        }

    def __collections_exceptions(self, name):
        return {
            Variable   : lambda: DuplicatedVariableException('Duplicated variable {0}'.format(name)),
            Alias      : lambda: DuplicatedAliasException('Duplicated alias {0}'.format(name)),
            Model      : lambda: DuplicatedModelException('Duplicated model {0}'.format(name)),
            Message    : lambda: DuplicatedMessageException('Duplicated message {0}'.format(name)),
            Resource   : lambda: DuplicatedResourceException('Duplicated resource {0}'.format(name)),
            Service    : lambda: DuplicatedServiceException('Duplicated service {0}'.format(name)),
            Reservation: lambda: DuplicatedReservationException('Duplicates reservation: {0}'.format(name)),
        }

    @property
    def fullname(self):
        return 'Schema'

    @property
    def variables(self):
        return self.__variables

    @property
    def aliases(self):
        return self.__aliases

    @property
    def models(self):
        return self.__models

    @property
    def messages(self):
        return self.__messages

    @property
    def resources(self):
        return self.__resources

    @property
    def services(self):
        return self.__services

    @property
    def reservations(self):
        return self.__reservations

    def add(self, arg):
        collections = self.__collections()
        collection = collections[type(arg)]
        if type(arg) is Reservation:
            collection.add(arg)
        else:
            for _collection in collections.values():
                if arg.name in _collection:
                    raise self.__collections_exceptions(arg.name)[type(arg)]
            collection[arg.name] = arg

    def visit_models(self, parentbefore=False):
        for model in self.models.values():
            if parentbefore:
                yield model
                yield from model.visit_models(parentbefore=parentbefore)
            else:
                yield from model.visit_models(parentbefore=parentbefore)
                yield model

    def merge(self, schema: 'Schema') -> None:
        for collection in schema.__collections().values():
            for item in (collection.values() if isinstance(collection, dict) else collection):
                self.add(item)

    def build_model_graph(self, modelcontainer):

        def finddatastruct(fullname: list, datastruct, index=0):
            if len(fullname) > index:
                if not isinstance(datastruct, (Schema, Model)):
                    raise Exception('Data struct is neither a schema nor a model: {0}'.format(datastruct.fullname))
                if fullname[index] not in datastruct.models and fullname[index] not in datastruct.enums:
                    raise DataStructNotFoundException('Data struct not found: {0}'.format(fullname))
                subdatastruct = datastruct.models[fullname[index]] if fullname[index] in datastruct.models else datastruct.enums[fullname[index]]
                return finddatastruct(fullname, subdatastruct, index=index + 1)
            return datastruct

        for model in modelcontainer.models.values():
            for field in model.fields.values():
                if field.id > 0:
                    if field.id in self.reservations:
                        raise ReservedIdInUseException("A reserved ID was used: {0} = {1}".format(field.fullname, field.id))
                    if field.id in self.__mapped_fields:
                        raise IdAlreadyInUseException("ID already in use: {0} = {1}".format(field.fullname, field.id))
                    self.__mapped_fields[field.id] = field

                    if '.'.join(field.datatype) in self.aliases:
                        field.datatype = self.aliases[field.datatype].value

                    if isinstance(field.datatype, list) and len(field.datatype) == 1 and field.datatype[0] in self.aliases:
                        field.datatype = self.aliases[field.datatype[0]]

                    if not isinstance(field.datatype, str):
                        refdatastruct = finddatastruct(field.datatype, self)
                        field.datatype = refdatastruct
                        backref_name = reduce(lambda a, b: b if len(a) == 0 else a, (x if x is not None else '' for x in list(re.match(r'"(.*?)"|\'(.*?)\'', field.modifiers.get('backref', '""')).groups()) + ['{0}_set'.format(model.fullname.lower())]))
                        reverse_reference_field = Field(backref_name, - field.id, field.parent, 'repeated', parent=refdatastruct)
                        refdatastruct.add_field(reverse_reference_field)

                    self.build_model_graph(modelcontainer=model)

    def build_message_graph(self, messagecontainer):

        def finddatastruct(fullname: list, datastruct, index=0):
            if len(fullname) > index:
                if not isinstance(datastruct, (Schema, Message)):
                    raise Exception('Data struct is neither a schema nor a message: {0}'.format(datastruct.fullname))
                if fullname[index] not in datastruct.messages and fullname[index] not in datastruct.enums:
                    raise DataStructNotFoundException('Data struct not found: {0}'.format(fullname))
                subdatastruct = datastruct.messages[fullname[index]] if fullname[index] in datastruct.messages else datastruct.enums[fullname[index]]
                return finddatastruct(fullname, subdatastruct, index=index + 1)
            return datastruct

        for message in messagecontainer.messages.values():
            for field in message.fields.values():

                if field.datatype in self.aliases:
                    field.datatype = self.aliases[field.datatype].value

                if field.id is not None:
                    if isinstance(field.datatype, str):  # mapped raw type field
                        if field.id not in self.__mapped_fields:
                            raise UnknownFieldMappingException('Unknown field mapping: {0} = {1}'.format(field.fullname, field.id))
                        if field.datatype not in DATA_TYPES:
                            raise UnknownDataTypeException('Unknown data type: {0} [{1}]'.format(field.datatype, field.fullname))
                        mapped_model_field = self.__mapped_fields[field.id]
                        if field.datatype != mapped_model_field.datatype:
                            raise DataTypeMismatchException('Data type mismatch: {0} -> {1} = {2}'.format(field.fullname, mapped_model_field.fullname, field.id))
                        field.model_field(mapped_model_field)
                    else:  # mapped message or enum field (not permitted)
                        raise TypeError('Within a message only raw type fields can be mapped: {0}'.format(field.fullname))
                elif field.id <= 0:
                    raise FieldException('Only explicitly defined fields could be used for mapping: {0} = {1}'.format(field.fullname, field.id))
                else:
                    if isinstance(field.datatype, str):  # unmapped raw type field
                        if field.datatype not in DATA_TYPES:
                            raise UnknownDataTypeException('Unknown data type: {0} [{1}]'.format(field.datatype, field.fullname))
                    else:  # unmapped message or enum field
                        refdatastruct = finddatastruct(field.datatype, self)
                        field.datatype = refdatastruct
                        # creates a backward reference from the destination message to the field message (the origin)
                        # not sure if it's a good idea...
                        # reverse_reference_field = Field('{0}_set'.format(message.fullname.lower()), None, field.parent, 'repeated', parent=refdatastruct)
                        # refdatastruct.add_message(reverse_reference_field)

                self.build_message_graph(messagecontainer=message)

    def validate_resources(self):

        def findmessage(fullname: list, datastruct=self, index=0) -> Message:
            if len(fullname) > index:
                if not isinstance(datastruct, (Schema, Message)):
                    raise Exception('Data struct is neither a schema nor a message: {0}'.format(datastruct.fullname))
                if fullname[index] not in datastruct.messages:
                    raise DataStructNotFoundException('Unknown message: {0}'.format('.'.join(fullname)))
                return findmessage(fullname, datastruct=datastruct.messages[fullname[index]], index=index + 1)
            return datastruct

        def checkdatatype(value, endpoint):
            if isinstance(value, str):
                if value not in DATA_TYPES and value != 'void':
                    raise UnknownDataTypeException('Unknown data type: {0} [{1}]'.format(value, endpoint.fullname))
                return value
            elif isinstance(value, list):
                return findmessage(value, datastruct=self)
            else:
                raise NotImplemented('Unknown datatype: {0} [{1}]'.format(value, endpoint.fullname))

        for resource in self.resources.values():
            for endpoint in resource.endpoints.values():
                endpoint.payload  = checkdatatype(endpoint.payload, endpoint)
                endpoint.response = checkdatatype(endpoint.response, endpoint)

    def validate_services(self):

        def finddatastruct(fullname: str, datastruct=self, index=0):
            if len(fullname) > index:
                if not isinstance(datastruct, (Schema, Model, Message)):
                    raise Exception('Data struct is neither a schema nor a model nor a message: {0}'.format(datastruct.fullname))
                if fullname[index] in datastruct.models:
                    return finddatastruct(fullname, datastruct=datastruct.models[fullname[index]], index=index + 1)
                elif fullname[index] in datastruct.messages:
                    return finddatastruct(fullname, datastruct=datastruct.messages[fullname[index]], index=index + 1)
                else:
                    raise DataStructNotFoundException('Unknown datastruct: {0}'.format('.'.join(fullname)))
            return datastruct

        def checkdatatype(value, method):
            if isinstance(value, str):
                if value not in DATA_TYPES and value != 'void':
                    raise UnknownDataTypeException('Unknown data type: {0} [{1}]'.format(value, method))
                return value
            elif isinstance(value, list):
                return finddatastruct(value, datastruct=self)
            else:
                raise NotImplemented('Unknown service datatype: {0} [{1}.{2}]'.format(datatype, method.service.name, method.name))

        for service in self.services.values():
            for method in service.methods.values():
                method.response = checkdatatype(method.response, method)
                for argname, datatype in method.attrs.items():
                    method.attrs[argname] = checkdatatype(datatype, method)


def cli(*args, **kwargs):
    config_filepath = 'config.json'
    if any(args):
        config_filepath = args[0]
    else:
        if not os.path.exists(config_filepath):
            raise Exception('Could not find the default configuration file: {0} not found in current directory'.format(
                config_filepath))
    config = ConfigStruct(config_filepath)
    config.build()


if __name__ == '__main__':
    t1 = datetime.now()

    cli(*sys.argv[1:])

    t2 = datetime.now()
    print('{0}Benchmark: {1}\n'.format('\n' * 5, t2 - t1))
