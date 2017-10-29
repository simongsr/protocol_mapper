#!/usr/bin/env python3
import os

import jinja2

# from filters import core
# from filters import python
from filters import sqlalchemy

__author__  = 'Simone Pandolfi'
__email__   = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


__TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
__ENVIRONMENT   = jinja2.Environment(
    loader=jinja2.FileSystemLoader(__TEMPLATES_DIR), trim_blocks=True, lstrip_blocks=True)
# __ENVIRONMENT.filters.update(core.FILTERS)
# __ENVIRONMENT.filters.update(python.FILTERS)
__ENVIRONMENT.filters.update(sqlalchemy.FILTERS)


# def pprint(obj):
#     import pprint
#     pp = pprint.PrettyPrinter(indent=True, depth=4)
#     pp.pprint(obj)


def build(schema, **kwargs):
    __create_outdir_if_not_exists(**kwargs)
    build_models(schema, **kwargs)
    # build_enums(schema, **kwargs)
    # build_messages(schema, **kwargs)


def __create_outdir_if_not_exists(outdir=os.path.dirname(__file__), **kwargs):
    if not os.path.exists(outdir):
        os.makedirs(outdir)


def __gen_enums(schema):
    return (obj for obj in core.enums(schema))


def __gen_models(schema):
    return (obj for obj in core.root_models(schema))


# def __gen_messages(schema):
#     return (obj for obj in core.root_messages(schema))


def build_models(schema, outdir, **kwargs):
    # pprint(schema['objects']['MioEnum'])
    output_filename = 'models.py'
    template        = __ENVIRONMENT.get_template(output_filename)
    context         = {
        # 'enums' : __gen_enums(schema),
        # 'models': __gen_models(schema),
        'schema': schema,
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


# def build_enums(schema, outdir, **kwargs):
#     output_filename = 'enums.py'
#     template        = __ENVIRONMENT.get_template(output_filename)
#     context         = {
#         'enums': __gen_enums(schema),
#     }
#     source          = template.render(context)
#     with open(os.path.join(outdir, output_filename), 'w') as fp:
#         fp.write(source)


# def build_messages(schema, outdir, **kwargs):
#     output_filename = 'messages.py'
#     template        = __ENVIRONMENT.get_template(output_filename)
#     context         = {
#         'messages': __gen_messages(schema),
#     }
#     source          = template.render(context)
#     with open(os.path.join(outdir, output_filename), 'w') as fp:
#         fp.write(source)
