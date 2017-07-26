import logging

from conf.appconfig import APP_NAME

logger = logging.getLogger(APP_NAME)


def task(func):
    def wrapper():
        name = '%s.%s' % (func.__module__, func.__name__)
        try:
            logger.info('Start task: %s', name)
            result = func()
            logger.info('Task: %s completed', name)
            return result
        except Exception as e:
            logger.error('Task: %s failed. Error: %s', name, str(e))

    return wrapper
