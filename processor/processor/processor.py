import json
import os
import socket
import time
import logging.config
import urllib.request
from random import randint
from urllib.error import URLError

from conf.appconfig import APP_NAME, TASK_REQUEST_URL, PROCESSOR, HEADERS
from conf.logconfig import LOGGING_CFG
from tasks.cook import CookTask



CAPABILITIES = [
    'calculate-prime-number',
    'calculate-triangular-number',
    'nyquist-plot',
    'cook-pasta'
]



cookTask = CookTask()

IMPLEMENTATIONS = {
    'cook-pasta': cookTask
}


def check_for_task():
    data = json.dumps({'processor': PROCESSOR, 'capabilities': CAPABILITIES}).encode('utf-8')
    req = urllib.request.Request(TASK_REQUEST_URL, data=data, headers=HEADERS)
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode('utf-8'))


def main():
    logging.config.dictConfig(LOGGING_CFG)
    logger = logging.getLogger(APP_NAME)

    while True:
        snooze = randint(1, 10)
        try:
            task = check_for_task()
            logger.info('Got new task: %s', json.dumps(task))
            IMPLEMENTATIONS[task['name']].process(task)
            print('sleeping for %d' % snooze)
        except URLError as e:
            logger.error('URLError: %s', str(e))
        logger.info('Sleeping for %d seconds...', snooze)
        time.sleep(snooze)


if __name__ == '__main__':
    main()
