import json

from apps.webapp import TaskManagerInputError
from conf.appconfig import ENQ_REQ_KEYS


def validate_task(task):
    if not ENQ_REQ_KEYS.issubset(set(task.keys())):
        raise TaskManagerInputError('Required keys missing in input')
    return task


