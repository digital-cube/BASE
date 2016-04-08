import mandrill
import base_config.settings
from base_config.service import log


def get_mail_api():
    try:
        return mandrill.Mandrill(base_config.settings.MAIL_API_KEY)
    except ValueError as e:
        log.critical('Missing or invalid mail API key: {}'.format(e))
        return False


# def send_message(sender, sender_name, _to, _to_name, subject, message, _site=None, tags=None):
def send_message(sender, _to, subject, message):

    receiver = [{'email': _to, 'name': _to, 'type': 'to'}]
    msg = {
        'from_email': sender,
        'from_name': sender,
        'html': message,
        'subject': subject,
        'to': receiver,
        # 'auto_html': None,        # automatic html generating if html not provided
        # 'auto_text': None,        # automatic text generating if text not provided
        # 'bcc_address': 'message.bcc_address@example.com', # bcc address
        # 'headers': {'Reply-To': 'message.reply@example.com'}, # additional headers
        # 'inline_css': None,       # if css has to be inline (only for <=256 line messages)
        # 'preserve_recipients': None,  # if every receiver has to see other receivers in header
        # 'text': 'Example text content',   # message plain text
        # 'view_content_link': None     # False for disable content logging for sensitive mails
    }
    # if _site:
    #     msg['metadata'] = {'website': _site}
    # if tags:
    #     msg['tags'] = tags

    m = get_mail_api()
    try:
        res = m.messages.send(message=msg, async=False)
    except mandrill.Error as e:
        log.critical('MANDRILL send message error: {}'.format(e))
        return False

    if 'status' not in res or res['status'] != 'sent':
        log.warning('MANDRILL send mail error status: {}'.format(res))
        return False

    log.info('Receiver: {}, status: {}'.format(_to, res))
    return True


def set_message_sent(id_message, svc_port):
    log.info('Set {} sent'.format(id_message))

    import json
    import datetime
    from base_svc.comm import BaseAPIRequestHandler

    n = str(datetime.datetime.now())[:19]

    rh = BaseAPIRequestHandler()
    data = {'id_message': id_message, 'sent_time': n}
    rh.set_argument('data', json.dumps(data))
    kwargs = {}
    kwargs['request_handler'] = rh

    from base_svc.comm import call
    import base_api.mail_api.sent_mail

    try:
        res, status = call(
            'localhost',
            # base_config.settings.APP_PORT,
            svc_port,
            base_api.mail_api.sent_mail.location,
            data,
            base_api.mail_api.sent_mail.set_mail_sent.__api_method_type__)
    except ConnectionRefusedError as e:
        log.critical('Servis not working: {}'.format(e))
        return False

    if status != 204:
        log.error('Error set message {} sent: {}'.format(id_message, res))

    return True

