#!/usr/bin/env python3.5
from pprint import PrettyPrinter

__author__ = 'Simone Pandolfi <simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


def make(params, environment):
    print(10 * '-' + ' python_django ' + 10 * '-')

    pp = PrettyPrinter(indent=True)
    pp.pprint(environment)
    pp.pprint(params)
