import base.application.lookup.session_token_type as stt


def get_token():
    return {'token_type': stt[stt.SIMPLE], 'token': 'asdfasdfaf'}
