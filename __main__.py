#!/usr/bin/env python3.5
from datetime import datetime

import sys

from main import cli

__author__  = 'Simone Pandolfi'
__email__   = '<simopandolfi@gmail.com>'
__version__ = (0, 0, 1)


if __name__ == '__main__':
    t1 = datetime.now()

    cli(*sys.argv[1:])

    t2 = datetime.now()
    print('{0}Benchmark: {1}\n'.format('\n' * 5, t2 - t1))
