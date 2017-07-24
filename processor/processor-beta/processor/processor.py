import json
import os
import socket
import time
import logging.config
import urllib.request
from random import randint
from urllib.error import URLError

from conf.appconfig import APP_NAME, TASK_REQUEST_URL
from conf.logconfig import LOGGING_CFG

PROCESSOR = {
    'host': socket.gethostname(),
    'pid': os.getpid(),
    'name': 'Issac Newton'
}

CAPABILITIES = [
    'calculate-prime-number',
    'calculate-triangular-number',
    'nyquist-plot',
    'cook-pasta'
]

HEADERS = {
    'Content-Type': 'application/json'
}


def check_for_task():
    data = json.dumps({'processor': PROCESSOR, 'capabilities': CAPABILITIES}).encode('utf-8')
    req = urllib.request.Request(TASK_REQUEST_URL, data=data, headers=HEADERS)
    res = urllib.request.urlopen(req)
    return res


def main():
    logging.config.dictConfig(LOGGING_CFG)
    logger = logging.getLogger(APP_NAME)

    while True:
        try:
            task = check_for_task()
            print(task)
            print('processing task')
            print('updating status')
            print('sleeping for %d' % snooze)
            time.sleep(snooze)
        except URLError as e:
            logger.error('URLError: %s', str(e))
        snooze = randint(1, 10)
        logger.info('Sleeping for %d seconds...', snooze)
        time.sleep(snooze)


if __name__ == '__main__':
    main()
