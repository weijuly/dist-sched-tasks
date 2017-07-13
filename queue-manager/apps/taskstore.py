import json
import logging
import os

import sqlite3
import time

from conf.appconfig import APP_NAME
from conf.dbconfig import QUERY_DROP_TABLE, QUERY_CREATE_TABLE, QUERY_NEXT_ELIGIBLE_TASK, QUERY_CREATE_TASK, \
    QUERY_CLEAR_TABLE, QUERY_SET_TASK_IN_PROGRESS, QUERY_VALIDATE_TASK, QUERY_SET_TASK_COMPLETE

TASK_INCOMPLETE = 0
TASK_IN_PROGRESS = 1
TASK_COMPLETE = 2

SET_TASK_REQUIRED_KEYS = set(['name', 'schedule', 'config'])


class TaskStoreError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def epoch():
    return int(time.time())


def obj2jsonstring(object):
    return json.dumps(object)


def generate_uuid(name, schedule, db_id):
    return '%s|%d|%d' % (name, schedule, db_id)


class TaskStore:
    def __init__(self, database, setup=False):
        self.logger = logging.getLogger(APP_NAME)
        self.database = database
        self.connection = sqlite3.connect(self.database)
        self.connection.set_trace_callback(self.logger.debug)
        self.cursor = self.connection.cursor()
        if setup:
            self.setup()
        self.logger.info('TaskStore initialized')

    def setup(self):
        self.cursor.execute(QUERY_DROP_TABLE)
        self.logger.info('Dropped queue table')
        self.cursor.execute(QUERY_CREATE_TABLE)
        self.logger.info('Created queue table')

    def destroy(self):
        self.connection.close()
        os.remove(self.database)
        self.logger.info('Database %s destroyed', self.database)

    def get(self, capabilities):
        capabilities = self.validate_capabilities(capabilities)
        query = QUERY_NEXT_ELIGIBLE_TASK % (epoch(), capabilities)
        self.cursor.execute(query)
        self.logger.info('Fetch next eligible task for capabilities: %s', capabilities)
        task = self.cursor.fetchone()
        if not task:
            self.raise_error('No task found matching capabilities: %s' % capabilities)
        name, config, uuid, schedule = task[1], json.loads(task[4]), generate_uuid(task[1], task[5], task[0]), task[5]
        return {
            'name': name,
            'args': config,
            'uuid': uuid,
            'schedule': schedule
        }

    def put(self, task):
        name, config, schedule = self.validate_task(task)
        self.cursor.execute(QUERY_CREATE_TASK, (name, epoch(), 0, config, schedule))
        self.connection.commit()
        uuid = generate_uuid(name, schedule, self.cursor.lastrowid)
        self.logger.info('Created task uuid:%s schedule: %d config %s', uuid, schedule, config)
        return uuid

    def mark_in_progress(self, uuid):
        queue_id = self.validate_uuid(uuid)
        self.cursor.execute(QUERY_SET_TASK_IN_PROGRESS, (queue_id,))
        self.connection.commit()
        self.logger.info('Task uuid: %s marked in progress', uuid)

    def mark_complete(self, uuid, result, processor):
        queue_id = self.validate_uuid(uuid)
        if type(result) is not dict or type(processor) is not dict:
            self.raise_error('result and processor should be dict')
        self.cursor.execute(QUERY_SET_TASK_COMPLETE, (epoch(), json.dumps(result), json.dumps(processor), queue_id))
        self.connection.commit()
        self.logger.info('Task uuid: %s marked in progress', uuid)

    def cleanup(self):
        self.cursor.execute(QUERY_CLEAR_TABLE)
        self.connection.commit()
        self.logger.info('All tasks cleared')

    def validate_capabilities(self, capabilities):
        if type(capabilities) is not list:
            self.raise_error('Capabilities should be a list')
        if len(capabilities) == 0:
            self.raise_error('Capabilities should not be empty')
        if False in map(lambda x: type(x) is str, capabilities):
            self.raise_error('Capabilities should be a list of string')
        return ','.join(['"%s"' % x for x in capabilities])

    def validate_uuid(self, uuid):
        if uuid.count('|') != 2:
            self.raise_error('UUID should be of format task|schedule|index, supplied: %s' % uuid)
        name, schedule, queue_id = uuid.split('|')
        schedule, queue_id = int(schedule), int(queue_id)
        self.cursor.execute(QUERY_VALIDATE_TASK, (queue_id, name, schedule))
        if self.cursor.fetchone() is None:
            self.raise_error('Task uuid: %s does not exist' % uuid)
        return queue_id

    def validate_task(self, task):
        if type(task) is not dict:
            self.raise_error('Task should be a dict')
        if not SET_TASK_REQUIRED_KEYS.issubset(set(task.keys())):
            self.raise_error('Task should contain name, schedule and config')
        return task['name'], obj2jsonstring(task['config']), task['schedule']

    def raise_error(self, message):
        self.logger.error(message)
        raise TaskStoreError(message)
