import json
import logging

from conf.appconfig import APP_NAME

logger = logging.getLogger(APP_NAME)


class RetryError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def decorate(retry=0):
    def outer(task):
        def inner(args):
            name = task.__module__
            logger.info('Starting task: %s, args: %s, max retry: %d', name, json.dumps(args), retry)
            max_attempts = retry + 2
            for attempt in range(1, max_attempts):
                try:
                    logger.info('Task: %s, attempt: %d', name, attempt)
                    result = task(args)
                    logger.info('Task: %s completed, attempt: %d', name, attempt)
                    return {'success': True, 'result': result}
                except RetryError as e:
                    logger.error('Task: %s failed, RetryError: %s, retry: %d', name, str(e), attempt)
                    continue
                except Exception as e:
                    logger.error('Task: %s failed, Exception: %s, cannot retry', name, str(e))
                    return {'success': False, 'error': str(e)}
            else:
                return {'success': False, 'error': 'retry count exceeded'}

        return inner

    return outer
