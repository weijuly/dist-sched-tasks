from utils.common import TaskQueueInputError
from conf.appconfig import ENQ_REQ_KEYS


def validate_task(task):
    if not ENQ_REQ_KEYS.issubset(set(task.keys())):
        raise TaskQueueInputError('Required keys missing in input')
    return task


