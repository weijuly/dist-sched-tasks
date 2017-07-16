import sys
import logging.config
import logging
from conf.appconfig import APP_NAME
from conf.logconfig import APP_LOGGING_CFG
from apps import persistence, subscriber, publisher, webapp

logging.config.dictConfig(APP_LOGGING_CFG)
logger = logging.getLogger(APP_NAME)

USAGE = '''
==============================================================================
# TASK MANAGER

Usage:
    python3 main.py [module] [action]

Module: persistence
    Action: setup
    Setup database instance for queue
    
    



==============================================================================
'''

MODULES = {
    'persistence': persistence.main,
    'delegate': publisher.main,
    'queue-manager': webapp.main
}

app = webapp.app


def main(args):
    if len(args) < 2:
        logger.error('Insufficient arguments passed')
        print(USAGE)
        return
    if args[1] not in MODULES:
        logger.error('No module by the name %s found' % args[1])
        print(USAGE)
        return
    if MODULES[args[1]](args[2:]) == -1:
        print(USAGE)
        return


if __name__ == '__main__':
    main(sys.argv)
