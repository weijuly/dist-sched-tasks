from conf.appconfig import APP_NAME

LOGGING_CFG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s : %(message)s'
        }
    },
    'handlers': {
        'handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/queue-manager.log',
            'maxBytes': 5*1024*1024,
            'backupCount': 10,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        APP_NAME: {
            'handlers': ['handler'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
