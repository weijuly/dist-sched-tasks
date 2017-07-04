import json
import sqlite3
from pathlib import Path

import zmq
import time
import logging

from conf.appconfig import JOB_SERVER, APP_NAME, CONTROL_FILE
from conf.dbconfig import DATABASE, QUERY_NEXT_ELIGIBLE_TASK, \
    QUERY_SET_TASK_IN_PROGRESS, QUERY_SET_TASK_COMPLETE, \
    QUERY_SET_TASK_INCOMPLETE

TASK_REQUEST = 0
TASK_STATUS = 1


def operation_type(request):
    if request['operation'] == 'request':
        return TASK_REQUEST
    if request['operation'] == 'status':
        return TASK_STATUS
    return TASK_REQUEST


def success(request):
    if request['success']:
        return True
    return False


def enabled():
    if Path(CONTROL_FILE).is_file():
        return True
    return False


class TaskServer:
    def __init__(self):
        self.logger = logging.getLogger(APP_NAME)
        self.logger.info('Initalizing task server...')
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(JOB_SERVER)
        self.logger.info('Task server listening at: %s', JOB_SERVER)
        self.connection = sqlite3.connect(DATABASE)
        self.cursor = self.connection.cursor()
        self.logger.info('Task server connected to database: %s', DATABASE)

    def serve(self):
        self.logger.info('Task server serving tasks')
        while True:
            try:
                if not enabled():
                    self.logger.info('Control turned off. Exiting...')
                    return
                self.handle()
            except Exception as e:
                self.logger.error('Exception occurred while serving request: %s', str(e))

    def handle(self):
        request = self.socket.recv_json()
        self.logger.info('Task server got request: %s', json.dumps(request))
        if operation_type(request) == TASK_REQUEST:
            task = self.fetch_next_eligible_task(request)
            if task:
                self.set_task_in_progress(task)
                self.socket.send_json(task)
            else:
                self.send_noop()
        if operation_type(request) == TASK_STATUS:
            self.logger.info('Task status reported: %s', json.dumps(request))
            if success(request):
                self.set_task_complete(request)
            else:
                self.set_task_incomplete(request)
            self.socket.send_json({'status': 'ack', 'time': int(time.time())})

    def fetch_next_eligible_task(self, request):
        epoch = int(time.time())
        capabilities = ','.join(['"%s"' % x for x in request['processor']['capabilities']])
        query = QUERY_NEXT_ELIGIBLE_TASK % (epoch, capabilities)
        self.cursor.execute(query)
        self.logger.info('Fetch next eligible task')
        self.logger.debug(query)
        task = self.cursor.fetchone()
        if not task:
            return None
        return {
            'task': task[1],
            'args': json.loads(task[4]),
            'uuid': task[0]
        }

    def set_task_in_progress(self, task):
        query = QUERY_SET_TASK_IN_PROGRESS % task['uuid']
        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info('Set task as processing')
        self.logger.debug(query)

    def set_task_complete(self, request):
        self.cursor.execute(QUERY_SET_TASK_COMPLETE, (int(time.time()),
                                                      json.dumps(request['details']),
                                                      json.dumps(request['processor']),
                                                      request['uuid']))
        self.logger.info('Set task as completed. uuid: %d', request['uuid'])

    def set_task_incomplete(self, request):
        query = QUERY_SET_TASK_INCOMPLETE % (request['uuid'])
        self.cursor.execute(query)
        self.connection.commit()
        self.logger.warning('Set task as incomplete. uuid %d', request['uuid'])
        self.logger.debug(query)

    def send_noop(self):
        self.logger.warning('No eligible tasks found: sending no-op to processor')
        self.socket.send_json({'task': '--noop--', 'args': {'random': 'string'}, 'uuid': 0})


def main(args):
    server = TaskServer()
    server.serve()
