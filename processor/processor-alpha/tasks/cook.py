import logging.config
import time

from conf.appconfig import APP_NAME
from utils.decorators import decorate, RetryError


@decorate(retry=1)
def main(config):
    logger = logging.getLogger(APP_NAME)
    logger.info('Cooking pasta')
    time.sleep(2)
    #raise RetryError('Gas temporarily not available')
    return {'message': 'cooking complete'}
