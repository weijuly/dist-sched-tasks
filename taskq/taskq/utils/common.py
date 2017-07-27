import json
import time


class TaskQueueInputError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TaskQueueSystemError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TaskQueueEmptyError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def epoch():
    return int(time.time())


def obj2jsonstring(object):
    return json.dumps(object)


def generate_uuid(name, schedule, db_id):
    return '%s|%d|%d' % (name, schedule, db_id)
