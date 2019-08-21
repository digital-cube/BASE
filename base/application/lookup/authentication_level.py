# coding= utf-8

STRONG = 1
WEAK = 2

lmap = {}
lmap[STRONG] = 'STRONG'
lmap[WEAK] = 'WEAK'

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k
