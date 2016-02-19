"""
Application specific hooks will be added to this module, or
existing will be overloaded if needed
check_password_is_valid -- validate given password (parameters: password) (user_register)
post_register_digest -- post register users data processing
                        (parameters: users id, username, password, json users data) (user_register)
prepare_user_query -- prepare query for insert user in db
                        (parameters: users id, username, password, json users data) (user_register)
pack_user_by_id -- get user from db by it's id (db connection, user id, application log) (dbtokens)
"""


def prepare_user_query(u_id, username, password, *args, **kwargs):
    """
    User registration query
    :param u_id:  user's id (unique)
    :param username:  user's username
    :param password:  given password
    :param args:  additional arguments (application specific)
    :param kwargs:  additional named arguments (application specific)
    :return:
    """

    q = "INSERT into users (id, username, password, active) VALUES " \
        "('{}', '{}', '{}', true)".format(
                u_id,
                username,
                password)

    return q


def pack_user_by_id(db, user_id, log, get_dict=False):
    """
    Pack users information in DBUser class instance
    :param db: database
    :param user_id: users id
    :param log: application log
    :param get_dict: export user like DBUser or dict
    :return: DBUser instance or user dict
    """

    dbc = db.cursor()
    q = "select id, username, password from users where id = '{}'".format(user_id)

    import MySQLdb
    try:
        dbc.execute(q)
    except MySQLdb.IntegrityError as e:
        log.critical('Error find user by token: {}'.format(e))
        return False

    if dbc.rowcount != 1:
        log.critical('Fount {} users with id {}'.format(dbc.rowcount, u_id))
        return False

    class DBUser:

        def dump_user(self):
            ret = {}
            for k in self.__dict__:
                if self.__dict__[k]:
                    ret[k] = self.__dict__[k]

            return ret

    db_user = DBUser

    user = dbc.fetchone()
    db_user.user_id = user['id']
    db_user.username = user['username']
    db_user.password = user['password']

    return db_user.dump_user() if get_dict else db_user


