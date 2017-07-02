import json
import logging.config
import os
import socket as sock

import zmq

from conf.appconfig import JOB_SERVER, APP_NAME
from conf.logconfig import LOGGING_CFG
from tasks import cook, shop

TASK_CAPABILITIES = {
    'cook': cook,
    'shop': shop
}


def main():
    logging.config.dictConfig(LOGGING_CFG)
    logger = logging.getLogger(APP_NAME)

    logger.info('Connecting to job server...')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(JOB_SERVER)
    logger.info('Connected to job server at: %s' % JOB_SERVER)

    processor = {
        'hostname': sock.gethostname(),
        'pid': os.getpid(),
        'app': APP_NAME,
        'capabilities': list(TASK_CAPABILITIES.keys())
    }
    logger.info('Processor: %s', json.dumps(processor))

    for i in range(2):
        try:
            request = {
                'operation': 'request',
                'processor': processor
            }
            socket.send_json(request)
            logger.info('Requesting task...')
            response = socket.recv_json()
            logger.info('Task: %s', json.dumps(response))
            task, args, uuid = response['task'], response['args'], response['uuid']
            result = TASK_CAPABILITIES[task].main(args)
            if not result['success']:
                logger.error('Task execution failed: %s', json.dumps(result))
            logger.info('Updating task status to job server...')
            request = {
                'operation': 'status',
                'processor': processor,
                'result': result,
                'uuid': uuid
            }
            socket.send_json(request)
            response = socket.recv_json()
            logger.info('Update complete. Server response: %s', json.dumps(response))
        except ValueError as e:
            logger.error('Job server responded with non-json message: ValueError: %s', str(e))
        except KeyError as e:
            logger.error('Job server responded with invalid message: KeyError: %s', str(e))


if __name__ == '__main__':
    main()
