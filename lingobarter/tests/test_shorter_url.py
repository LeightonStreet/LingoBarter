#!/usr/bin/env python
# coding: utf-8

import unittest

from lingobarter import create_app
from lingobarter.utils.shorturl import ShorterURL


class TestShorterUrl(unittest.TestCase):
    def create_app(self):
        # create_app return a tuple, app object is at index 0
        return create_app(config='lingobarter.test_settings',
                          DEBUG=False,
                          test=True)[0]

    def test_usage(self):
        url = 'http://google.com'
        app = self.create_app()
        with app.app_context():
            shorter = ShorterURL()
            self.assertIsNotNone(shorter)
            self.assertIsNotNone(shorter.short(url))