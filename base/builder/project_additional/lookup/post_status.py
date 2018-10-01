"""
Status of the post
"""

DRAFT = 1
IN_REVIEW = 2
PUBLISHED = 3

lmap = {
    DRAFT: 'DRAFT',
    IN_REVIEW: 'IN_REVIEW',
    PUBLISHED: 'PUBLISHED',
}

lrev = dict((v, k) for k, v in lmap.items())

