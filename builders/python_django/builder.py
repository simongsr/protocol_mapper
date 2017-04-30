#!/usr/bin/env python3.5
import os
from pprint import PrettyPrinter

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


def build(environment, **kwargs):
    # print(10 * '-' + ' python_django ' + 10 * '-')
    # pp = PrettyPrinter(indent=True)
    # pp.pprint(environment)
    # pp.pprint(kwargs)

    __create_outdir_if_not_exists(**kwargs)
    __build_models(environment, **kwargs)


def __create_outdir_if_not_exists(outdir=os.path.dirname(__file__)):
    if not os.path.exists(outdir):
        os.mkdir(outdir)


def __build_models(env, outdir=None):
    template = __ENVIRONMENT.get_template('models.py')
    context  = {
        'models'  : [obj for obj in core.root_models(env)],
        'messages': [obj for obj in core.root_messages(env)],
        # TODO inserire anche i root enums
    }
    source   = template.render(context)
    print(source)
    with open(os.path.join(outdir, 'models.py'), 'w') as fp:
        fp.write(source)
