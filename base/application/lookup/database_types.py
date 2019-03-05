# coding= utf-8

MYSQL = 1
POSTGRESQL = 2
SQLITE = 3

lmap = {}
lmap[MYSQL] = 'MYSQL'
lmap[POSTGRESQL] = 'POSTGRESQL'
lmap[SQLITE] = 'SQLITE'

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k
