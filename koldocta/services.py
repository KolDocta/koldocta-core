# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/koldocta/license


class BaseService():
    '''
    Base service for all endpoints, defines the basic implementation
    for CRUD datalayer functionality.
    '''
    datasource = None

    def __init__(self, datasource=None, backend=None):
        self.backend = backend
        self.datasource = datasource

    def on_create(self, docs):
        pass

    def on_created(self, docs):
        pass

    def on_update(self, updates, original):
        pass

    def on_updated(self, updates, original):
        pass

    def on_replace(self, document, original):
        pass

    def on_replaced(self, document, original):
        pass

    def on_delete(self, doc):
        pass

    def on_deleted(self, doc):
        pass

    def on_fetched(self, doc):
        pass

    def on_fetched_item(self, doc):
        pass

    def is_authorized(self, **kwargs):
        """
        Subclass should override if the resource handled by the service has intrinsic privileges.
        :param kwargs: should have properties which help in authorizing the request
        :return: False if unauthorized and True if authorized
        """

        return True
