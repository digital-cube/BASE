"""
Available languages.
Request a language with url parameter like:
@api(
    URI="/:__LANG__/other_part_of_the_url",
    PREFIX=False
)

this will match path: "/(en|rs|de)/other_part_of_the_url",
and expect the language in the params (language_url_param_name):
@params(
    {'name': 'language', 'type': str, 'doc': 'chosen language'},
)
"""

EN = 1
RS = 2
DE = 3

lmap = {
    EN: 'en',
    RS: 'rs',
    DE: 'de',
}

lrev = dict((v, k) for k, v in lmap.items())

languages_map = {
    lmap[EN]: 'English',
    lmap[RS]: 'Serbian',
    lmap[DE]: 'German'
}

language_url_param_name = 'language'
