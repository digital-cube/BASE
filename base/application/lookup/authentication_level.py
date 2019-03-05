# coding= utf-8

STRONG = 1
WEEK = 2

lmap = {}
lmap[STRONG] = 'STRONG'
lmap[WEEK] = 'WEEK'

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k
