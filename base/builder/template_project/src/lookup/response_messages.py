# coding= utf-8

ERROR = 1000
EXCEPTION = 1001
MISSING_OPTION = 1002

lmap = {}
lmap[ERROR] = 'Error'
lmap[EXCEPTION] = 'Exception'
lmap[MISSING_OPTION] = 'Missing option'

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k
