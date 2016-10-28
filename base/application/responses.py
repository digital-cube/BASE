ERROR = 1
EXCEPTION = 2

map = {}
map[ERROR] = 'Error'
map[EXCEPTION] = 'Exception'

rev = {}
for k in map:
    rev[map[k]] = k

