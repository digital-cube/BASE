# coding= utf-8

SIMPLE = 1
EXCLUSIVE = 2
PARALLEL = 3

lmap = {}
lmap[SIMPLE] = 'Simple'
lmap[EXCLUSIVE] = 'Exclusive'
lmap[PARALLEL] = 'Parallel'

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k
