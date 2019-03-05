# coding= utf-8

DB = 1
REDIS = 2

lmap = {}
lmap[DB] = 'DB'
lmap[REDIS] = 'REDIS'

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k