import json
import logging
import urllib.request
from urllib.error import URLError

from conf.appconfig import APP_NAME, TASK_UPDATE_URL
from conf.appconfig import PROCESSOR, HEADERS


class Task:
    def __init__(self):
        self.logger = logging.getLogger(APP_NAME)

    def success(self, result, uuid):
        self.logger.info('Updating task as success')
        self.update(result, uuid)

    def failure(self, result, uuid):
        self.logger.info('Updating task as failure')
        self.update(result, uuid, False)

    def update(self, result, uuid, success=True):
        try:
            data = json.dumps({
                'processor': PROCESSOR,
                'result': result,
                'success': success,
                'uuid': uuid
            }).encode('utf-8')
            req = urllib.request.Request(TASK_UPDATE_URL, data=data, headers=HEADERS)
            res = urllib.request.urlopen(req)
        except URLError as e:
            self.logger.error('Update task status failure: %s', str(e))

