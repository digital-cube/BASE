# coding= utf-8

ERROR = 1
EXCEPTION = 2
GET_NOT_FOUND = 3
POST_NOT_FOUND = 4
PATCH_NOT_FOUND = 5
PUT_NOT_FOUND = 6
DELETE_NOT_FOUND = 7
API_CALL_EXCEPTION = 8
MISSING_REQUEST_ARGUMENT = 9
INVALID_REQUEST_ARGUMENT = 10
ARGUMENT_LOWER_THEN_MINIMUM = 11
ARGUMENT_HIGHER_THEN_MINIMUM = 12
HTTP_METHOD_NOT_ALLOWED = 13
USERNAME_ALREADY_TAKEN = 14
INVALID_PASSWORD = 15
ERROR_USER_REGISTER = 16
ERROR_USER_SEQUENCE = 17
ERROR_RETRIEVE_SESSION = 18
ERROR_USER_POSTREGISTER = 19
WRONG_USERNAME_OR_PASSWORD = 20

lmap = {}
lmap[ERROR] = 'Error'
lmap[EXCEPTION] = 'Exception'
lmap[GET_NOT_FOUND] = 'GET requested resource not found'
lmap[POST_NOT_FOUND] = 'POST requested resource not found'
lmap[PATCH_NOT_FOUND] = 'PATCH requested resource not found'
lmap[PUT_NOT_FOUND] = 'PUT requested resource not found'
lmap[DELETE_NOT_FOUND] = 'DELETE requested resource not found'
lmap[API_CALL_EXCEPTION] = 'Call Error'
lmap[MISSING_REQUEST_ARGUMENT] = "Missing request argument"
lmap[INVALID_REQUEST_ARGUMENT] = "Invalid request argument"
lmap[ARGUMENT_LOWER_THEN_MINIMUM] = "Argument is lower then minimum limit"
lmap[ARGUMENT_HIGHER_THEN_MINIMUM] = "Argument is higher then maximum limit"
lmap[HTTP_METHOD_NOT_ALLOWED] = "Not allowed"
lmap[USERNAME_ALREADY_TAKEN] = "Username already taken"
lmap[INVALID_PASSWORD] = "Invalid password"
lmap[ERROR_USER_REGISTER] = "Error registering user"
lmap[ERROR_USER_SEQUENCE] = "Error making user sequence"
lmap[ERROR_RETRIEVE_SESSION] = "Error getting a new token"
lmap[ERROR_USER_POSTREGISTER] = "Post-register error"
lmap[WRONG_USERNAME_OR_PASSWORD] = "Wrong username or password"

lrev = {}
for k in lmap:
    lrev[lmap[k]] = k

