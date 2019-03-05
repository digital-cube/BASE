# coding= utf-8
"""
This one is placeholder for users lookup.
User role flags for access levels.
DAU - developer admin user.
At least USER required.
"""


USER = 1

lmap = {}
lmap[USER] = 'USER'

lrev = dict((v, k) for k, v in lmap.items())
