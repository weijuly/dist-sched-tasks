import json
import logging.config
import os
import socket as sock

import time
from pathlib import Path

import zmq

from conf.appconfig import JOB_SERVER, APP_NAME, CONTROL_FILE
from conf.logconfig import LOGGING_CFG
from tasks import cook, shop

TASK_CAPABILITIES = {
    'cook': cook,
    'shop': shop
}

PROCESSOR = {
    'hostname': sock.gethostname(),
    'pid': os.getpid(),
    'app': APP_NAME,
    'capabilities': list(TASK_CAPABILITIES.keys())
}


def task_request():
    return {
        'operation': 'request',
        'processor': PROCESSOR
    }


def task_status(result, uuid):
    return {
        'operation': 'status',
        'processor': PROCESSOR,
        'details': result,
        'uuid': uuid,
        'success': result['success']
    }


def noop(task):
    if task == '--noop--':
        return True
    return False


def enabled():
    if Path(CONTROL_FILE).is_file():
        return True
    return False


def main():
    logging.config.dictConfig(LOGGING_CFG)
    logger = logging.getLogger(APP_NAME)

    logger.info('Connecting to job server...')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(JOB_SERVER)
    logger.info('Connected to job server at: %s' % JOB_SERVER)

    logger.info('Processor: %s', json.dumps(PROCESSOR))

    while True:
        try:
            if not enabled():
                logger.info('Control turned off. Exiting...')
                return
            socket.send_json(task_request())
            logger.info('Requesting task...')
            response = socket.recv_json()
            logger.info('Task: %s', json.dumps(response))
            task, args, uuid = response['task'], response['args'], response['uuid']
            if noop(task):
                time.sleep(5)
                continue
            result = TASK_CAPABILITIES[task].main(args)
            if not result['success']:
                logger.error('Task execution failed: %s', json.dumps(result))
            logger.info('Updating task status to job server...')
            socket.send_json(task_status(result, uuid))
            response = socket.recv_json()
            logger.info('Update complete. Server response: %s', json.dumps(response))
        except ValueError as e:
            logger.error('Job server responded with non-json message: ValueError: %s', str(e))
        except KeyError as e:
            logger.error('Job server responded with invalid message: KeyError: %s', str(e))


if __name__ == '__main__':
    main()
