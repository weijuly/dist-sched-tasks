import time
from random import randint

from common.task import Task


class CookTask(Task):
    def __init__(self):
        Task.__init__(self)

    def process(self, task):
        self.args = task['args']
        self.uuid = task['uuid']
        number = randint(1, 100)
        time.sleep(20)
        result = {'name': 'someone'}
        if number > 50:
            self.success(result, self.uuid)
        else:
            self.failure(result, self.uuid)
