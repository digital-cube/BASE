#!/usr/bin/env python3
# coding= utf-8

from base.application.service import engage
from base import __VERSION__

if __name__ == '__main__':
    if __VERSION__ > '1.0.1':
        engage(__file__)
    else:
        engage()

