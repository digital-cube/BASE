#!/usr/bin/env python3

import MySQLdb
from MySQLdb import IntegrityError, cursors
import json
import time
import sys
import sendgrid
from config.shortenerconfig import log
import datetime

def get_mail_query_ok(id_msg, msg_datetime, res_msg):

    q = '''UPDATE mail_queue set sent = true, time_sent = '{}', data = '{}' WHERE id = {} '''.format(str(msg_datetime), res_msg, id_msg)

    return q

def get_mail_query_err(id_msg, msg_datetime, res_msg):

    q = '''UPDATE mail_queue set sent = FALSE , time_sent = '{}', data = '{}' WHERE id = {} '''.format(str(msg_datetime), res_msg, id_msg)

    return q


def conn_to_db():
    return MySQLdb.connect(
    host='localhost',
    user='shorty',
    passwd='123',
    db='shortener',  # Promenjeno za potrebe TESTA
    charset='utf8',
    cursorclass=MySQLdb.cursors.DictCursor)

q = '''SELECT id, receiver, message FROM mail_queue ORDER BY id desc LIMIT 1'''


if __name__ == '__main__':

    single_shot = '-s' in sys.argv
    log.info('STARTING mail sender {}'.format(' in single shot mode' if single_shot else ''))

    try:
        svc_port = int(sys.argv[1])
    except ValueError as e:
        print('Invalid value for port {}, has to be int '.format(sys.argv[1]))
        sys.exit(1)

    while True:

        db = conn_to_db()
        dbc = db.cursor()

        try:
            dbc.execute(q)
        except IntegrityError as e:
            print('Query didnt execute correctly Q: {} : {}'.format(q, e))
            continue
        if dbc.rowcount == 0:
            print("There is no work to be done")
            if single_shot:
                sys.exit()
            time.sleep(5)
            continue

        else:

            res = dbc.fetchone()
            receiver = res['receiver']
            emsg = res['message']
            id_msg = res['id']

            sg = sendgrid.SendGridClient('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')

            id = 1
            from_email = 'Min.bz@digitalcube.rs'
            from_name = 'Min.bz URL Shorterner'
            to_email = receiver
            to_name = receiver
            subject = 'Registration'
            _message = emsg

            try:

                message = sendgrid.Mail()
                message.add_to('{} <{}>'.format(to_name, to_email))
                message.set_subject(subject)
                message.set_html(_message)
                message.set_text(_message)
                message.set_from('{} <{}>'.format(from_name, from_email))
                status, msg = sg.send(message)

                print(msg)
                print(status)
            except Exception as e:
                print(e)

            res_msg = json.loads(msg.decode('utf-8'))
            res_msg = res_msg['message']

            n = str(datetime.datetime.now())[:19]

            if status == 200:
                q = get_mail_query_ok(id_msg, n, res_msg)

            else:
                q = get_mail_query_err(id_msg, n, res_msg)


            try:
                dbc.execute(q)
            except IntegrityError as e:
                log.critical('Update mail queue: {}'.format(e))

            db.commit()


            if single_shot:
                sys.exit()

            time.sleep(5)
