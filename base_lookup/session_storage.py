# -*- coding: utf-8 -*-

DB = 1
REDIS = 2

map_ = {}
map_['DB'] = DB
map_['REDIS'] = REDIS

rev = dict((y, x) for (x, y) in map_.items())
