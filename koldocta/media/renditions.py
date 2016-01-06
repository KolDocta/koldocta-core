# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/koldocta/license

from __future__ import absolute_import
import logging
from flask import current_app as app

logger = logging.getLogger(__name__)


def delete_file_on_error(doc, file_id):
    # Don't delete the file if we are on the import from storage flow
    if doc.get('_import', None):
        return
    app.media.delete(file_id)
