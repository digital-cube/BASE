# coding= utf-8

ERROR = 1000
EXCEPTION = 1001

lmap = {}
lmap[ERROR] = 'Error'
lmap[EXCEPTION] = 'Exception'

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k
