"""
Application specific hooks will be added to this module, or
existing will be overloaded if needed
check_password_is_valid -- validate given password (parameters: password) (user_register)
post_register_digest -- post register users data processing
                        (parameters: users id, username, password, json users data) (user_register)
prepare_user_query -- prepare query for insert user in db
                        (parameters: users id, username, password, json users data) (user_register)
"""


def prepare_user_query(u_id, username, password, *args, **kwargs):

    q = "INSERT into users (id, username, password) VALUES " \
            "('{}', '{}', '{}')".format(
                u_id,
                username,
                password)

    return q


