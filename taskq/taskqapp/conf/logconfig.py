import logging

from conf.appconfig import APP_NAME, WEB

APP_LOGGING_CFG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s: %(message)s'
        },
        'web': {
            'format': '%(asctime)s: %(message)s'
        }
    },
    'handlers': {
        'appLogHandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
        'webLogHandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/web.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'web'
        }
    },
    'loggers': {
        APP_NAME: {
            'handlers': ['appLogHandler'],
            'level': 'DEBUG',
            'propagate': True
        },
        WEB: {
            'handlers': ['webLogHandler'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}
