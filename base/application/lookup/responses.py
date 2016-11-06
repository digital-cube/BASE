# coding= utf-8

ERROR = 1
EXCEPTION = 2
GET_NOT_ALLOWED = 3
POST_NOT_ALLOWED = 4
PATCH_NOT_ALLOWED = 5
PUT_NOT_ALLOWED = 6
DELETE_NOT_ALLOWED = 7
API_CALL_EXCEPTION = 8

lmap = {}
lmap[ERROR] = 'Error'
lmap[EXCEPTION] = 'Exception'
lmap[GET_NOT_ALLOWED] = 'GET not allowed'
lmap[POST_NOT_ALLOWED] = 'POST not allowed'
lmap[PATCH_NOT_ALLOWED] = 'PATCH not allowed'
lmap[PUT_NOT_ALLOWED] = 'PUT not allowed'
lmap[DELETE_NOT_ALLOWED] = 'DELETE not allowed'
lmap[API_CALL_EXCEPTION] = 'Call Error'

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k

