import time

from common.task import Task


class CookTask(Task):
    def __init__(self):
        Task.__init__(self)

    def generate(self):
        for flavor in ['lasange', 'spaghetti', 'macaroni', 'cannelloni']:
            self.task = {
                'name': 'cook-pasta',
                'schedule': int(time.time()) + 300,
                'config': {
                    'flavor': flavor,
                    'quantity': 2
                }
            }
        self.enqueue()


cookTask = CookTask()
