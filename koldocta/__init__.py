# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Koldocta"""

from flask import abort, json, Blueprint, current_app as app  # noqa
from flask.ext.script import Command as BaseCommand, Option  # noqa @UnresolvedImport
from werkzeug.exceptions import HTTPException
from eve.utils import config  # noqa
from eve.methods.common import document_link  # noqa

from .services import BaseService
from .resource import Resource  # noqa
import logging

API_NAME = 'KolDocta API'
VERSION = (0, 0, 1)
DOMAIN = {}
COMMANDS = {}
BLUEPRINTS = []
JINJA_FILTERS = dict()
app_components = dict()
app_models = dict()
resources = dict()
_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    The Eve framework changes introduced with https://github.com/nicolaiarocci/eve/issues/213 make the commands fail.
    Reason being the flask-script's run the commands using test_request_context() which is invalid.
    That's the reason we are inheriting the Flask-Script's Command to overcome this issue.
    """
    logger = _logger

    def __call__(self, _app=None, *args, **kwargs):
        try:
            with app.app_context():
                res = self.run(*args, **kwargs)
                self.logger.info('Command finished with: {}'.format(res))
                return 0
        except Exception as ex:
            self.logger.info('Uhoh, an exception occured while running the command...')
            self.logger.exception(ex)
            return 1


def domain(resource, res_config):
    """Register domain resource"""
    DOMAIN[resource] = res_config


def command(name, command):
    """Register command"""
    COMMANDS[name] = command


def blueprint(blueprint, **kwargs):
    """Register blueprint"""
    blueprint.kwargs = kwargs
    BLUEPRINTS.append(blueprint)


def register_resource(name, resource, service=None):
    """Shortcut for registering resource and service together.

    :param name: resource name
    :param resource: resource class
    :param service: service class
    """
    if not service:
        service = BaseService
    service_instance = service(name)
    resource(name, app=app, service=service_instance)


def register_jinja_filter(name, jinja_filter):
    """
    Register jinja filter
    :param str name: name of the filter
    :param jinja_filter: jinja filter function
    """
    JINJA_FILTERS[name] = jinja_filter
