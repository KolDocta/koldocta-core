# -*- coding: utf-8; -*-
#
# This file is part of Koldocta.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/koldocta/license

from koldocta.tests import TestCase


# TODO test validators
class KoldoctaValidatorTest(TestCase):
    """Base class for the KoldoctaValidator class tests."""

    def setUp(self):
        super(KoldoctaValidatorTest, self).setUp()
        klass = self._get_target_class()
        self.validator = klass(schema={})
        self.validator.document = {}
        self._errors = {}

    def _get_target_class(self):
        """Return the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from koldocta.validator import KoldoctaValidator
        except ImportError:
            self.fail("Could not import class under test (KoldoctaValidator)")
        else:
            return KoldoctaValidator
