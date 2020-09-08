import json
import base.registry
from base import http
import redis
import datetime
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

from base import Base

from tornado.httpclient import AsyncHTTPClient

from orm.orm import orm_session
import orm.models as models
import sendgrid


@Base.route(URI="/about")
class AboutMailerServiceHandler(Base.BASE):

    @Base.api()
    async def get(self):
        return {'service': 'mailer'}



@Base.route(URI="")
class MailerServiceHandler(Base.BASE):
    executor = ThreadPoolExecutor(max_workers=32)

    @run_on_executor
    def sendgrid_send_email(self, sender, sender_name, receiver, receiver_name, subject, message):
        if '@' not in receiver:
            return True

        sendgrid_api_key = base.registry.service('mailer')['sendgrid_api_key']
        sg = sendgrid.SendGridAPIClient(sendgrid_api_key)
        mail = {
            'personalizations': [
                {
                    'to': [
                        {
                            'email': receiver,
                            'name': receiver_name
                        }
                    ],
                    'subject': subject
                }
            ],
            'from': {
                'email': sender,
                'name': sender_name
            },
            'content': [
                {
                    'type': 'text/html',
                    'value': message
                }
            ]
        }
        try:
            response = sg.send(mail)
        except Exception as e:
            return False

        return True

    # Ne koristi se async / await vec thread executor jer se poziva sg.send a ne Asynchttp client

    @Base.api()
    @gen.coroutine
    def put(self, mail: models.Mailqueue):
        self.orm_session.add(mail)
        self.orm_session.commit()
        res = self.sendgrid_send_email(mail.sender_email, mail.sender_name, mail.receiver_email, mail.receiver_name,
                                       mail.subject, mail.body)

        return {'id': mail.id}, http.code.HTTPStatus.CREATED
