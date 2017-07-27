import urllib.request
import json
from urllib.error import URLError

import logging

from conf.appconfig import APP_NAME, TASK_ENQUEUE_URL

HEADERS = {
    'Content-Type': 'application/json'
}


class Task:
    def __init__(self):
        self.logger = logging.getLogger(APP_NAME)
        self.task = None

    def enqueue(self):
        if not self.task:
            self.logger.error('No task to enqueue')
            return
        try:
            data = json.dumps(self.task).encode('utf-8')
            self.logger.info('Enqueueing task: %s', data)
            req = urllib.request.Request(TASK_ENQUEUE_URL, data=data, headers=HEADERS)
            res = urllib.request.urlopen(req)
        except URLError as e:
            self.logger.error('URLError while enqueueing task: %s', str(e))
        except ValueError as e:
            self.logger.error('ValueError while enqueueing task: %s', str(e))
