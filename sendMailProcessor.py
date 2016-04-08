import sys
import json
from base_config.service import log
import base_common.dbacommon
import base_config.settings
import base_common.send_mail_common as smcommon

__SVC_PORT = int(sys.argv[1])


if __name__ == '__main__':

    dbr = base_common.dbacommon.get_redis_db()

    blocked = False
    while not blocked:
        task = dbr.brpop(base_config.settings.MAIL_CHANNEL, base_config.settings.MAIL_CHANNEL_TIMEOUT)

        if task is not None:

            task = task[1].decode('utf-8')  # tuple 0-channel, 1-task
            task = json.loads(task)
            log.info('got: {}'.format(task['id']))

            if not smcommon.send_message(task['sender'], task['receiver'], task['subject'], task['message']):
                log.critical('Error sending message: {}'.format(task['id']))
                continue

            if not smcommon.set_message_sent(task['id'], __SVC_PORT):
                blocked = True
