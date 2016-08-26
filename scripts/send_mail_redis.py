#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sys
import time
import json
import urllib

import MySQLdb
import MySQLdb.cursors
import sendgrid
from MySQLdb import IntegrityError, OperationalError
import redis

# from send_mail_config import log, db_host, db_user, db_passwd, db_name, db_charset, sg_key
# from send_mail_config import REDIS_PORT, REDIS_SERVER

MAIL_NOT_SENT = 0
MAIL_ON_SENDING = 1
MAIL_SUCCESSFULLY_SENT = 2
MAIL_SENT_ERROR = 3


from base_svc.comm import call

# def call(svc_url, port, location, data, method, request_timeout=10, force_json=False, call_headers=None):
#     import http.client
#     conn = http.client.HTTPConnection(svc_url, port)
#
#     if force_json:
#         body = json.dumps(data, ensure_ascii=False)
#         _headers = {'content-type': 'application/json'}
#     else:
#         body = urllib.parse.urlencode(data)
#         _headers = {'content-type': 'application/x-www-form-urlencoded'}
#
#     if call_headers:
#         _headers.update(call_headers)
#
#     conn.request(method, "/" + location, body, headers=_headers)
#
#     response = conn.getresponse()
#     return response.read().decode('utf-8'), response.status

def get_mail_query_ok(id_msg, msg_datetime, status, mdata):
    return '''UPDATE mail_queue set sent = {}, time_sent = '{}', data = '{}' WHERE id = {} '''.format(
        status, str(msg_datetime), mdata, id_msg)

def get_mail_query_err(id_msg, msg_datetime, status, mdata):
    return '''UPDATE mail_queue set sent = {}, time_sent = '{}', data = '{}' WHERE id = {} '''.format(
        status, str(msg_datetime), mdata, id_msg)

def get_redis_db(res):

    __redis = redis.Redis(host=res['REDIS_SERVER'], port=res['REDIS_PORT'])

    return __redis

def conn_to_db(res):
    db = MySQLdb.connect(
        db=res['db_name'],
        host=res['db_host'],
        user=res['db_user'],
        passwd=res['db_passwd'],
        charset=res['db_charset'],
        cursorclass=MySQLdb.cursors.DictCursor)

    # cursor = db.cursor()
    # try:
    #     cursor.execute("SELECT VERSION()")
    #     results = cursor.fetchone()
    #
    # except MySQLdb.Error:
    #     print ("Error in db connection")

    return db

def execute_query(query,db,dbConnData,attempt):
    try:
        dbc = db.cursor()
        dbc.execute(query)
        db.commit()
    except OperationalError as e:
        if attempt>5:
            return False
        db = conn_to_db(dbConnData)
        attempt = attempt + 1;
        print ('reconnecting to database...{}'.format(attempt))
        execute_query(query,db,dbConnData,attempt)

if __name__ == '__main__':

    try:
        svc_port = int(sys.argv[1])

    except ValueError as e:
        print('Invalid value for port {}, has to be int '.format(sys.argv[1]))
        sys.exit(1)

    res = call('localhost', svc_port, 'params', {}, 'GET', request_timeout=10, force_json=False, call_headers=None)
    _res = res[0]
    __res = json.loads(_res)

    import logging
    from logging.handlers import TimedRotatingFileHandler

    log_filename = __res['send_mail_log']
    log_handler = TimedRotatingFileHandler(log_filename, when="midnight")
    log_formatter = logging.Formatter(
        '%(asctime)-6s %(name)s %(module)s %(funcName)s %(lineno)d - %(levelname)s %(message)s')
    log_handler.setFormatter(log_formatter)

    _log = __res['_log']
    log = logging.getLogger(_log)
    log.propagate = False
    log.addHandler(log_handler)
    log.setLevel(logging.DEBUG)

    single_shot = '-s' in sys.argv

    log.info('STARTING mail sender {}'.format(' in single shot mode' if single_shot else ''))

    r = get_redis_db(__res)

    db = conn_to_db(__res)
    dbc = db.cursor()

    while True:

        task = r.brpop('BSM {}'.format(svc_port), 5)
        if task:
            log.info('Task found, working')
            t = task[1]
            mail_to_send = json.loads(t.decode('utf-8'))

            sender = mail_to_send['sender']
            sender_name = mail_to_send['sender_name']
            receiver = mail_to_send['receiver']
            receiver_name = mail_to_send['receiver_name']
            subject = mail_to_send['subject']
            emsg = mail_to_send['message']

            # mdata = mail_to_send['data']
            id_msg = mail_to_send['id']

            try:
                mdata = json.loads(mdata)
            except:
                mdata = {}

            sg = sendgrid.SendGridAPIClient(apikey=__res['sg_key'])

            from sendgrid.helpers.mail import *
            message = Mail()
            personal = Personalization()
            message.set_from(Email(sender, sender_name))
            personal.add_to(Email(receiver, receiver_name))
            message.add_personalization(personal)
            message.set_subject(subject)
            message.add_content(Content("text/html", emsg))
            m_data = message.get()
            response = sg.client.mail.send.post(request_body=m_data)

            print(response, type(response))
            m_id = response.headers.get('X-Message-Id')
            if m_id:
                mdata['message_id'] = m_id

            res_msg = response.body.decode('utf-8')
            n = str(datetime.datetime.now())[:19]

            try:
                mdata['send_result'] = res_msg
                mdata = json.dumps(mdata, ensure_ascii=False)
            except Exception as e:
                print('ERROR PREPARING MESSAGE DATA |{}|{}| FOR DATABASE: {}'.format(mdata, res_msg, e))
                mdata = json.dumps(mdata, ensure_ascii=False)  # just save it like it was before

            status = MAIL_ON_SENDING
            if 200 <= response.status_code < 300:
                status = MAIL_SUCCESSFULLY_SENT
                q = get_mail_query_ok(id_msg, n, status, mdata)

            else:
                status = MAIL_SENT_ERROR
                q = get_mail_query_err(id_msg, n, status, mdata)

            try:
                attempt = 0
                execute_query(q,db,__res,attempt)
            except IntegrityError as e:
                log.critical('Update mail queue: {}'.format(e))


        else:
            print("There is no work to be done")
            if single_shot:
                sys.exit()


