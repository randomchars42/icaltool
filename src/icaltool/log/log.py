#!/usr/bin/env python3

config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s',
        },
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        #'file':{
        #    'level': 'DEBUG',
        #    'class': 'logging.handlers.RotatingFileHandler',
        #    'filename': 'log',
        #    'formatter': 'detailed',
        #    'maxBytes': 1024,
        #    'backupCount': 5,
        #    }
    },
    'loggers': {
        '__main__': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'icstool': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
    }
}
