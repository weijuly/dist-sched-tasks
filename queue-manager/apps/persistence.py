import logging

import sqlite3

from conf.appconfig import APP_NAME
from conf.dbconfig import QUERY_DROP_TABLE, QUERY_CREATE_TABLE, QUERY_CLEAR_TABLE, DATABASE
from utils.decorators import task

logger = logging.getLogger(APP_NAME)


@task
def setup():
    connection = sqlite3.connect(DATABASE)
    logger.info('Connected to %s', DATABASE)
    cursor = connection.cursor()
    cursor.execute(QUERY_DROP_TABLE)
    logger.info('Success %s', QUERY_DROP_TABLE)
    cursor.execute(QUERY_CREATE_TABLE)
    logger.info('Success %s', QUERY_CREATE_TABLE)


@task
def cleanup():
    connection = sqlite3.connect(DATABASE)
    logger.info('Connected to %s', DATABASE)
    cursor = connection.cursor()
    cursor.execute(QUERY_CLEAR_TABLE)
    logger.info('Success %s', QUERY_CLEAR_TABLE)


ACTIONS = {
    'setup': setup,
    'cleanup': cleanup
}


def main(args):
    action = args[0]
    if action not in ACTIONS:
        logger.error('Action: %s not found', action)
        return
    ACTIONS[action]()
