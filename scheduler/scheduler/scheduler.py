import logging.config
import schedule
import time

from conf.appconfig import APP_NAME, SNOOZE
from conf.logconfig import LOGGING_CFG

from tasks.cook import cookTask

logging.config.dictConfig(LOGGING_CFG)
logger = logging.getLogger(APP_NAME)


schedule.every(1).minutes.do(cookTask.generate)

while True:
    logger.info('Running pending tasks')
    schedule.run_pending()
    logger.info('Sleeping for %d seconds', SNOOZE)
    time.sleep(SNOOZE)
