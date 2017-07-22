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
    __build_models(schema, **kwargs)
    __build_admin(schema, **kwargs)
    __build_urls(schema, **kwargs)
    __build_views(schema, **kwargs)


def __create_outdir_if_not_exists(outdir=os.path.dirname(__file__), **kwargs):
    if not os.path.exists(outdir):
        os.makedirs(outdir)


def __build_models(schema, outdir, **kwargs):
    output_filename = 'models.py'
    template        = __ENVIRONMENT.get_template(output_filename)
    context         = {
        'enums'   : (obj for obj in core.enums(schema)),
        'models'  : (obj for obj in core.root_models(schema)),
        'messages': (obj for obj in core.root_messages(schema)),
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


def __build_admin(schema, outdir, appname="", **kwargs):
    output_filename = 'admin.py'
    template        = __ENVIRONMENT.get_template(output_filename)
    context         = {
        'env'    : schema,
        'appname': appname,
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


def __build_urls(schema, outdir, **kwargs):
    output_filename = 'urls.py'
    template        = __ENVIRONMENT.get_template(output_filename)
    context         = {
        'urls': {
            name: core.build_uri(endpoint['modifiers']['url'], schema['vars'])
                 for name, endpoint in schema['endpoints'].items()
        },
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


def __build_views(schema, outdir, **kwargs):
    output_filename = 'views.py'
    template = __ENVIRONMENT.get_template(output_filename)
    context = {
        'enums': (obj for obj in core.enums(schema)),
        'models': (obj for obj in core.root_models(schema)),
        'messages': (obj for obj in core.root_messages(schema)),
    }
    source = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)
