#!/usr/bin/env python3.5
import os

import jinja2

from filters import core
from filters import python
from filters import python_django

__author__  = 'Simone Pandolfi'
__email__   = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


__TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
__ENVIRONMENT   = jinja2.Environment(
    loader=jinja2.FileSystemLoader(__TEMPLATES_DIR), trim_blocks=True, lstrip_blocks=True)
__ENVIRONMENT.filters.update(core.FILTERS)
__ENVIRONMENT.filters.update(python.FILTERS)
__ENVIRONMENT.filters.update(python_django.FILTERS)


def build(schema, **kwargs):
    __create_outdir_if_not_exists(**kwargs)
    build_models(schema, **kwargs)
    build_enums(schema, **kwargs)
    build_admin(schema, **kwargs)
    build_urls(schema, **kwargs)
    build_views(schema, **kwargs)
    build_messages(schema, **kwargs)


def __create_outdir_if_not_exists(outdir=os.path.dirname(__file__), **kwargs):
    if not os.path.exists(outdir):
        os.makedirs(outdir)


def __gen_enums(schema):
    return (obj for obj in core.enums(schema))


def __gen_models(schema):
    return (obj for obj in core.root_models(schema))


def __gen_messages(schema):
    return (obj for obj in core.root_messages(schema))


def __gen_endpoints(schema):
    return (obj for obj in core.endpoints(schema)
            if core.extract_string_value(obj['modifiers'].get('type', [''])[0]) == 'REST')


def build_models(schema, outdir, **kwargs):
    output_filename = 'models.py'
    template        = __ENVIRONMENT.get_template(output_filename)
    context         = {
        'enums'   : __gen_enums(schema),
        'models'  : __gen_models(schema),
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


def build_enums(schema, outdir, **kwargs):
    output_filename = 'enums.py'
    template        = __ENVIRONMENT.get_template(output_filename)
    context         = {
        'enums': __gen_enums(schema),
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


def build_admin(schema, outdir, appname="", **kwargs):
    output_filename = 'admin.py'
    template        = __ENVIRONMENT.get_template(output_filename)
    context         = {
        'env'    : schema,
        'appname': appname,
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


def build_urls(schema, outdir, **kwargs):
    output_filename = 'urls.py'
    template        = __ENVIRONMENT.get_template(output_filename)
    context         = {
        'urls': {
            endpoint['name']: core.build_uri(endpoint['modifiers']['url'], schema['vars'])
                 for endpoint in __gen_endpoints(schema)
        }
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


def build_views(schema, outdir, **kwargs):
    output_filename = 'views.py'
    template = __ENVIRONMENT.get_template(output_filename)
    context = {
        'enums'    : __gen_enums(schema),
        'models'   : __gen_models(schema),
        'messages' : __gen_messages(schema),
        'endpoints': __gen_endpoints(schema),
    }
    source = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


def build_messages(schema, outdir, **kwargs):
    output_filename = 'messages.py'
    template        = __ENVIRONMENT.get_template(output_filename)
    context         = {
        'messages': __gen_messages(schema),
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)
