GET = 1
PUT = 2
DELETE = 3
POST = 4
PATCH = 5

map = {}
map['GET'] = GET
map['PUT'] = PUT
map['DELETE'] = DELETE
map['POST'] = POST
map['PATCH'] = PATCH

rev = dict((y, x) for (x, y) in map.items())
