#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os
import logging
import importlib
import jinja2
import eve
import settings
import superdesk
from flask.ext.mail import Mail
from eve.io.mongo import MongoJSONEncoder
from eve.render import send_response
from superdesk.celery_app import init_celery
from eve.auth import TokenAuth
from superdesk.storage.desk_media_storage import SuperdeskGridFSMediaStorage
from superdesk.validator import SuperdeskValidator
from raven.contrib.flask import Sentry
from superdesk.errors import SuperdeskError, SuperdeskApiError
from superdesk.io import providers
from logging.handlers import SysLogHandler
sentry = Sentry(register_signal=False, wrap_wsgi=False)


def configure_logging(config):
    sys_handler = SysLogHandler(address=(config['LOG_SERVER_ADDRESS'], config['LOG_SERVER_PORT']))
    logging.basicConfig(handlers=[logging.StreamHandler(), sys_handler])
    logger = logging.getLogger('superdesk')
    logger.setLevel(logging.INFO)
    return logger


def get_app(config=None, media_storage=None):
    """App factory.

    :param config: configuration that can override config from `settings.py`
    :return: a new SuperdeskEve app instance
    """
    if config is None:
        config = {}

    config['APP_ABSPATH'] = os.path.abspath(os.path.dirname(__file__))

    for key in dir(settings):
        if key.isupper():
            config.setdefault(key, getattr(settings, key))

    if media_storage is None:
        media_storage = SuperdeskGridFSMediaStorage

    config['DOMAIN'] = {}
    logger = configure_logging(config)

    app = eve.Eve(
        data=superdesk.SuperdeskDataLayer,
        auth=TokenAuth,
        media=media_storage,
        settings=config,
        json_encoder=MongoJSONEncoder,
        validator=SuperdeskValidator)

    superdesk.app = app

    custom_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(['superdesk/templates'])
    ])
    app.jinja_loader = custom_loader

    app.mail = Mail(app)

    @app.errorhandler(SuperdeskError)
    def client_error_handler(error):
        """Return json error response.

        :param error: an instance of :attr:`superdesk.SuperdeskError` class
        """
        return send_response(None, (error.to_dict(), None, None, error.status_code))

    @app.errorhandler(500)
    def server_error_handler(error):
        """Log server errors."""
        app.sentry.captureException()
        logger.exception(error)
        return_error = SuperdeskApiError.internalError()
        return client_error_handler(return_error)

    init_celery(app)

    for module_name in app.config['INSTALLED_APPS']:
        app_module = importlib.import_module(module_name)
        try:
            app_module.init_app(app)
        except AttributeError:
            pass

    for resource in superdesk.DOMAIN:
        app.register_resource(resource, superdesk.DOMAIN[resource])

    for blueprint in superdesk.BLUEPRINTS:
        prefix = app.api_prefix or None
        app.register_blueprint(blueprint, url_prefix=prefix)

    # we can only put mapping when all resources are registered
    app.data.elastic.put_mapping(app)

    app.sentry = sentry
    sentry.init_app(app)

    # instantiate registered provider classes (leave non-classes intact)
    for key, provider in providers.items():
        providers[key] = provider() if isinstance(provider, type) else provider

    return app