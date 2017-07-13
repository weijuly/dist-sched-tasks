import sqlite3
from flask import Flask

from conf.appconfig import APP_NAME

app = Flask(__name__)

import logging

class TaskStore:
    def __init__(self, database):
        self.logger = logging.getLogger(APP_NAME)
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_next_eligible_task(self, capabilities):
        pass

    def mark_task_in_progress(self):
        pass

    def mark_task_complete(self):
        pass

    def mark_task_incomplete(self):
        pass

@app.route('/')
def index():
    return 'Hallo'
