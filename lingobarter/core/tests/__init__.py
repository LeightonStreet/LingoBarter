# coding: utf-8
from flask.ext.testing import TestCase

from lingobarter import create_app
from lingobarter.core.admin import create_admin


class BaseTestCase(TestCase):
    def create_app(self):
        self.admin = create_admin()
        # create_app return a tuple, app object is at index 0
        return create_app(config='lingobarter.test_settings',
                          admin_instance=self.admin,
                          test=True)[0]
