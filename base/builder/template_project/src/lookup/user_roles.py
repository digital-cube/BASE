"""
User role flags for access levels.
DAU - developer admin user.
At least USER required.
"""

DEVELOPER = 4
ADMIN = 2
USER = 1

lmap = {
    DEVELOPER: 'DEVELOPER',
    ADMIN: 'ADMIN',
    USER: 'USER',
}

lrev = dict((v, k) for k, v in lmap.items())
