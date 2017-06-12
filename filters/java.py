#!/usr/bin/env python3.5
from filters import core

__author__ = 'Simone Pandolfi'
__email__ = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


def class_name(obj):
    return '__'.join(obj['fullname']).title().replace('_', '')


FILTERS = {
    'java.class_name': class_name,
}
