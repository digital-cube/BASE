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
    res = {'status': 'sent'} # TODO: SKLONI OVO OBAVEZNO
    # try:
    #     res = m.messages.send(message=msg, async=False)
    # except mandrill.Error as e:
    #     log.critical('MANDRILL send message error: {}'.format(e))
    #     return False

    if 'status' not in res or res['status'] != 'sent':
        log.warning('MANDRILL send mail error status: {}'.format(res))
        return False

    log.info('Receiver: {}, status: {}'.format(_to, res))
    return True


def set_message_sent(id_message):
    log.info('Set {} sent'.format(id_message))
