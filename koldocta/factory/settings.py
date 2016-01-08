#!/usr/bin/env python
# -*- coding: utf-8; -*-
#

import os
import logging

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

def env(variable, fallback_value=None):
    env_value = os.environ.get(variable, '')
    if len(env_value) == 0:
        return fallback_value
    else:
        if env_value == "__EMPTY__":
            return ''
        else:
            return env_value


DEBUG = env('KOLDOCTA_DEBUG', True)
BANDWIDTH_SAVER = False
PAGINATION_LIMIT = 200

APPLICATION_NAME = env('APP_NAME', 'KolDocta')
server_url = urlparse(env('KOLDOCTA_URL', 'http://localhost:5000/api'))
URL_PROTOCOL = server_url.scheme or None
SERVER_NAME = server_url.netloc or None

URL_PREFIX = server_url.path.lstrip('/') or ''
if SERVER_NAME.endswith(':80'):
    SERVER_NAME = SERVER_NAME[:-3]

if ':' in SERVER_NAME: 
    parts = SERVER_NAME.split(':')
    SERVER_DOMAIN = parts[0]
else:
    SERVER_DOMAIN = SERVER_NAME

JSON_SORT_KEYS = True

MONGO_DBNAME = env('MONGO_DBNAME', 'koldocta')
MONGO_URI = env('MONGO_URI', 'mongodb://localhost/%s' % MONGO_DBNAME)

AMAZON_CONTAINER_NAME = env('AWS_CONTAINER_NAME', '')
AMAZON_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', 'XXXX')
AMAZON_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', 'XXXX')
AMAZON_REGION = env('AWS_REGION', 'us-west-1')
AMAZON_SERVE_DIRECT_LINKS = env('AWS_SERVE_DIRECT_LINKS', False)
AMAZON_S3_USE_HTTPS = env('AWS_S3_USE_HTTPS', False)


BROKER_BACKEND = "SQS"
BROKER_TRANSPORT_OPTIONS = {
    'region': AMAZON_REGION,
}
BROKER_USER = AMAZON_ACCESS_KEY_ID
BROKER_PASSWORD = AMAZON_SECRET_ACCESS_KEY
BROKER_URL = 'sqs://'

CELERY_ALWAYS_EAGER = (env('CELERY_ALWAYS_EAGER', False) == 'True')
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']  # it's using pickle when in eager mode
CELERY_IGNORE_RESULT = True
CELERYD_LOG_FORMAT = '%(message)s level=%(levelname)s process=%(processName)s'
CELERYD_TASK_LOG_FORMAT = ' '.join([CELERYD_LOG_FORMAT, 'task=%(task_name)s task_id=%(task_id)s'])

CELERYBEAT_SCHEDULE_FILENAME = env('CELERYBEAT_SCHEDULE_FILENAME', './celerybeatschedule.db')
CELERYBEAT_SCHEDULE = {

}

SENTRY_DSN = env('SENTRY_DSN', '')
SENTRY_ERROR_LEVEL = logging.WARNING
SENTRY_INCLUDE_PATHS = ['koldocta']

INSTALLED_APPS = [

    'koldocta.stats'
]

RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
EXTENDED_MEDIA_INFO = ['content_type', 'name', 'length']
RETURN_MEDIA_AS_BASE64_STRING = False


ORGANIZATION_NAME = "KolDocta Powered Service"
ORGANIZATION_NAME_ABBREVIATION = "KolDoc"
