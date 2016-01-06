# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/koldocta/license


import logging

from flask import current_app as app
from eve.validation import ValidationError


logger = logging.getLogger(__name__)
notifiers = []


def add_notifier(notifier):
    if notifier not in notifiers:
        notifiers.append(notifier)


def update_notifiers(*args, **kwargs):
    for notifier in notifiers:
        notifier(*args, **kwargs)


class KoldoctaError(ValidationError):
    _codes = {}
    system_exception = None

    def __init__(self, code, desc=None):
        """
        :param int code: numeric error code
        :param desc: optional detailed error description, defaults to None
        """
        self.code = code
        self.message = self._codes.get(code, 'Unknown error')
        self.desc = desc

    def __str__(self):
        desc_text = '' if not self.desc else (' Details: ' + self.desc)
        return "{} Error {} - {}{desc}".format(
            self.__class__.__name__,
            self.code,
            self.message,
            desc=desc_text
        )

    def get_error_description(self):
        return self.code, self._codes[self.code]


class KoldoctaApiError(KoldoctaError):
    """Base class for koldocta API."""

    # default error status code
    status_code = 400

    def __init__(self, message=None, status_code=None, payload=None):
        """
        :param message: a human readable error description
        :param status_code: response status code
        :param payload: a dict with request issues
        """
        Exception.__init__(self)
        self.message = message

        if status_code:
            self.status_code = status_code

        if payload:
            self.payload = payload

        logger.error("HTTP Exception {} has been raised: {}".format(status_code, message))

    def to_dict(self):
        """Create dict for json response."""
        rv = {}
        rv[app.config['STATUS']] = app.config['STATUS_ERR']
        rv['_message'] = self.message or ''
        if hasattr(self, 'payload'):
            rv[app.config['ISSUES']] = self.payload
        return rv

    def __str__(self):
        return "{}: {}".format(repr(self.status_code), self.message)

    @classmethod
    def badRequestError(cls, message=None, payload=None):
        return KoldoctaApiError(status_code=400, message=message, payload=payload)

    @classmethod
    def unauthorizedError(cls, message=None, payload={'auth': 1}):
        return KoldoctaApiError(status_code=401, message=message, payload=payload)

    @classmethod
    def forbiddenError(cls, message=None, payload=None):
        return KoldoctaApiError(status_code=403, message=message, payload=payload)

    @classmethod
    def notFoundError(cls, message=None, payload=None):
        return KoldoctaApiError(status_code=404, message=message, payload=payload)

    @classmethod
    def preconditionFailedError(cls, message=None, payload=None):
        return KoldoctaApiError(status_code=412, message=message, payload=payload)

    @classmethod
    def internalError(cls, message=None, payload=None):
        return KoldoctaApiError(status_code=500, message=message, payload=payload)


class IdentifierGenerationError(KoldoctaApiError):
    """Exception raised if failed to generate unique_id."""

    status_code = 500
    payload = {'unique_id': 1}
    message = "Failed to generate unique_id"


class InvalidFileType(KoldoctaError):
    """Exception raised when receiving a file type that is not supported."""

    def __init__(self, type=None):
        super(InvalidFileType, self).__init__('Invalid file type %s' % type, payload={})


class BulkIndexError(KoldoctaError):
    """Exception raised when bulk index operation fails.."""

    def __init__(self, resource=None, errors=None):
        super(BulkIndexError, self).__init__('Failed to bulk index resource {} errors: {}'.format(resource, errors), payload={})


class PrivilegeNameError(Exception):
    pass


class InvalidStateTransitionError(KoldoctaApiError):
    """Exception raised if workflow transition is invalid."""

    def __init__(self, message='Workflow transition is invalid.', status_code=412):
        super(InvalidStateTransitionError, self).__init__(message, status_code)

