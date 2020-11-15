#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import sys
import time

import MySQLdb
import MySQLdb.cursors
import sendgrid
from MySQLdb import IntegrityError

from send_mail_config import log, db_host, db_user, db_passwd, db_name, db_charset, sg_key

MAIL_NOT_SENT = 0
MAIL_ON_SENDING = 1
MAIL_SUCCESSFULLY_SENT = 2
MAIL_SENT_ERROR = 3


def get_mail_query_ok(id_msg, msg_datetime, status, mdata):
    q = '''UPDATE mail_queue set sent = {}, time_sent = '{}', data = '{}' WHERE id = {} '''.format(
        status, str(msg_datetime), mdata, id_msg)

    return q


def get_mail_query_err(id_msg, msg_datetime, status, mdata):
    q = '''UPDATE mail_queue set sent = {}, time_sent = '{}', data = '{}' WHERE id = {} '''.format(
        status, str(msg_datetime), mdata, id_msg)

    return q


def conn_to_db():

    return MySQLdb.connect(
        db=db_name,
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        charset=db_charset,
        cursorclass=MySQLdb.cursors.DictCursor)


if __name__ == '__main__':

    single_shot = '-s' in sys.argv
    log.info('STARTING mail sender {}'.format(' in single shot mode' if single_shot else ''))

    try:
        svc_port = int(sys.argv[1])
    except ValueError as e:
        print('Invalid value for port {}, has to be int '.format(sys.argv[1]))
        sys.exit(1)


    q = '''SELECT
            id, sender, sender_name, receiver, receiver_name, subject, message, data
          FROM
            mail_queue
          WHERE
            sent = {}'''.format(MAIL_NOT_SENT)

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

            for res in dbc.fetchall():

                sender = res['sender']
                sender_name = res['sender_name']
                receiver = res['receiver']
                receiver_name = res['receiver_name']
                subject = res['subject']
                emsg = res['message']

                if '@' not in sender or '@' not in receiver:
                    print('Can not send message: {}'.format(res))
                    continue

                mdata = res['data']
                id_msg = res['id']

                try:
                    mdata = json.loads(mdata)
                except:
                    mdata = {}

                sg = sendgrid.SendGridAPIClient(apikey=sg_key)
                # sg = sendgrid.SendGridClient(sg_key)

                # try:
                if True:
                    from sendgrid.helpers.mail import *

                    if sendgrid.__version__ > '3.x.x':
                        from_email = Email(sender, sender_name)
                        to_email = Email(receiver, receiver_name)
                        subject = subject
                        content = Content("text/html", emsg)
                        message = Mail(from_email, subject, to_email, content)
                        m_data = message.get()
                    else:
                        message = Mail()
                        personal = Personalization()
                        message.set_from(Email(sender, sender_name))
                        personal.add_to(Email(receiver, receiver_name))
                        message.add_personalization(personal)
                        message.set_subject(subject)
                        message.add_content(Content("text/html", emsg))
                        m_data = message.get()
                    try:
                        response = sg.client.mail.send.post(request_body=m_data)
                    except Exception as e:
                        print('ERROR SENDGRID POST:', e)
                        print('ERROR WITH MESSAGE:', res)
                        continue

                print(response, type(response))
                # except Exception as e:
                  #     print(e)
                # print('*****************************')
                # print(response.status_code, type(response.status_code))
                # print('*****************************')
                # print(response.headers, type(response.headers))
                m_id = response.headers.get('X-Message-Id')
                # print(m_id)
                # print('*****************************')
                # print(response.body, type(response.body))
                # print('*****************************')
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
                    dbc.execute(q)
                except IntegrityError as e:
                    log.critical('Update mail queue: {}'.format(e))

                db.commit()

                if single_shot:
                    sys.exit()

                time.sleep(0.5)

