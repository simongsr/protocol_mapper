#!/usr/bin/env python3.5
import os

import itertools
from collections import OrderedDict
from datetime import datetime

import copy
import jinja2

from filters import core
from filters import java
from filters import java_android
from main import make_model, make_model_field

__author__  = 'Simone Pandolfi'
__email__   = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


__TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
__ENVIRONMENT   = jinja2.Environment(
    loader=jinja2.FileSystemLoader(__TEMPLATES_DIR), trim_blocks=True, lstrip_blocks=True)
__ENVIRONMENT.filters.update(core.FILTERS)
__ENVIRONMENT.filters.update(java.FILTERS)
__ENVIRONMENT.filters.update(java_android.FILTERS)


def __titlize(string):
    return '' if len(string) == 0 else '{0}{1}'.format(string[0].title(), string[1:])


def build(environment, **kwargs):
    kwargs['outdir'] = __create_outdir_if_not_exists(**kwargs)
    schema           = __create_join_models(environment)
    __build_db_contract(env=schema, **kwargs)
    __build_db_helper(schema=schema, **kwargs)


def __create_outdir_if_not_exists(package, appname, outdir=os.path.dirname(__file__), **kwargs):
    if not isinstance(package, str):
        raise TypeError("Package must be string, got: {0}".format(type(package).__name__))
    if not isinstance(appname, str):
        raise TypeError("Appname must be string, got: {0}".format(type(appname).__name__))
    outdir = os.path.join(*itertools.chain([outdir, appname], package.split('.')))
    print(outdir, os.path.exists(outdir))
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    return outdir


def __create_join_models(env):
    schema = copy.deepcopy(env)

    def build_name(field):
        return 'join_{0}___{1}___{2}'.format('__'.join(field['parent']['fullname']).lower(),
                                             '__'.join(field['data_type']['fullname']).lower(),
                                             field['name'].lower())

    def find_container(model1, model2):
        if model1 == model2:
            return model1

        fullname1 = model1['fullname']
        fullname2 = model2['fullname']
        container_model = schema
        for i in range(min(len(fullname1), len(fullname2))):
            if fullname1[i] == fullname2[i]:
                name = fullname1[i]
                container_model = container_model['objects'][name]
        return container_model

    for model in core.models(env):
        for field in java_android.repeated_fields(model):
            if isinstance(field['data_type'], dict):
                owner_model           = field['parent']
                field_owner_column    = make_model_field(multiplicity='required',
                                                         datatype=field['parent'],
                                                         name='__'.join(owner_model['fullname']),
                                                         _id=0)
                field_datatype_column = make_model_field(multiplicity='required',
                                                         datatype=field['data_type'],
                                                         name='__'.join(field['data_type']['fullname']),
                                                         _id=0)
                join_model            = make_model(name=build_name(field), fields=OrderedDict([
                                            (field_owner_column['name'], field_owner_column),
                                            (field_datatype_column['name'], field_datatype_column)
                                        ]))
                container = find_container(model1=owner_model, model2=field['data_type'])
                container['objects'][join_model['name']] = join_model

    return schema


def __build_db_contract(env, outdir, package, appname, **kwargs):
    classname       = '{0}DbContract'.format(__titlize(appname))
    output_filename = '{0}.java'.format(classname)
    template        = __ENVIRONMENT.get_template('DbContract.java')
    context         = {
        'package'      : package,
        'now'          : datetime.now().isoformat(),
        'contract_name': classname,
        'schema'       : env,
    }
    source          = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


def __build_db_helper(schema, outdir, package, appname, **kwargs):
    classname = '{0}DbHelper'.format(__titlize(appname))
    output_filename = '{0}.java'.format(classname)
    template = __ENVIRONMENT.get_template('DbHelper.java')
    context = {
        'package'    : package,
        'appname'    : appname,
        'now'        : datetime.now().isoformat(),
        'helper_name': classname,
        'schema'     : schema,
    }
    source = template.render(context)
    with open(os.path.join(outdir, output_filename), 'w') as fp:
        fp.write(source)


# def __build_models(env, outdir=None, **kwargs):
#     output_filename = 'models.py'
#     template        = __ENVIRONMENT.get_template(output_filename)
#     context         = {
#         'enums'   : (obj for obj in core.enums(env)),
#         'models'  : (obj for obj in core.root_models(env)),
#         'messages': (obj for obj in core.root_messages(env)),
#     }
#     source          = template.render(context)
#     with open(os.path.join(outdir, output_filename), 'w') as fp:
#         fp.write(source)
#
#
# def __build_admin(env, outdir=None, appname="", **kwargs):
#     output_filename = 'admin.py'
#     template        = __ENVIRONMENT.get_template(output_filename)
#     context         = {
#         'env'    : env,
#         'appname': appname,
#     }
#     source          = template.render(context)
#     with open(os.path.join(outdir, output_filename), 'w') as fp:
#         fp.write(source)
