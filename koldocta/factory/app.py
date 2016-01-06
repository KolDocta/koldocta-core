#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/koldocta/license

import os
import importlib
import jinja2
import eve
import koldocta.factory.settings
from eve.io.mongo import MongoJSONEncoder
from eve.render import send_response
from koldocta.celery_app import init_celery
from eve.auth import TokenAuth
from koldocta.storage.desk_media_storage import KoldoctaGridFSMediaStorage
from raven.contrib.flask import Sentry
from koldocta.errors import KoldoctaError, KoldoctaApiError
import logging
from logging.handlers import SysLogHandler

sentry = Sentry(register_signal=False, wrap_wsgi=False)


def configure_logging(app, config):
    sys_handler = SysLogHandler(
        address=(config['LOG_SERVER_ADDRESS'], config['LOG_SERVER_PORT']))
    app.logger.addHandler(sys_handler)


def get_app(config=None, media_storage=None):
    """App factory.

    :param config: configuration that can override config from `settings.py`
    :return: a new SuperdeskEve app instance
    """
    if config is None:
        config = {}

    abs_path = os.path.abspath(os.path.dirname(__file__))
    config.setdefault('APP_ABSPATH', abs_path)

    for key in dir(koldocta.factory.settings):
        if key.isupper():
            config.setdefault(key, getattr(koldocta.factory.settings, key))

    if media_storage is None:
        media_storage = KoldoctaGridFSMediaStorage

    config.setdefault('DOMAIN', {})
   

    app = eve.Eve(
        media=media_storage,
        settings=config,
        json_encoder=MongoJSONEncoder,
    )
    configure_logging(app, config)
    koldocta.app = app

    custom_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader([abs_path + '/../templates'])
    ])
    app.jinja_loader = custom_loader

    @app.errorhandler(KoldoctaError)
    def client_error_handler(error):
        """Return json error response.

        :param error: an instance of :attr:`koldocta.KoldoctaError` class
        """
        return send_response(
            None, (error.to_dict(), None, None, error.status_code))

    @app.errorhandler(500)
    def server_error_handler(error):
        """Log server errors."""
        app.sentry.captureException()
        app.logger.exception(error)
        return_error = KoldoctaApiError.internalError()
        return client_error_handler(return_error)

    init_celery(app)

    for module_name in app.config['INSTALLED_APPS']:
        app_module = importlib.import_module(module_name)
        try:
            app_module.init_app(app)
        except AttributeError:
            app.logger.error('App %s not initialized' % (module_name))

    for resource in koldocta.DOMAIN:
        app.register_resource(resource, koldocta.DOMAIN[resource])

    for blueprint in koldocta.BLUEPRINTS:
        prefix = app.api_prefix or None
        app.register_blueprint(blueprint, url_prefix=prefix)

    for name, jinja_filter in koldocta.JINJA_FILTERS.items():
        app.jinja_env.filters[name] = jinja_filter

    app.sentry = sentry
    sentry.init_app(app)

    return app
