TOKEN = 1
COOKIE = 2

lmap = {}
lmap[TOKEN] = 'TOKEN'
lmap[COOKIE] = 'COOKIE'

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k
