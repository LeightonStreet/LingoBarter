#!/usr/bin/env python
# coding: utf-8

import unittest
from lingobarter.utils.shorturl import ShorterURL
from lingobarter import create_app


class TestShorterUrl(unittest.TestCase):
    def create_app(self):
        return create_app(config='lingobarter.test_settings',
                          DEBUG=False,
                          test=True)

    def test_usage(self):
        url = 'http://google.com'
        app = self.create_app()
        with app.app_context():
            shorter = ShorterURL()
            self.assertIsNotNone(shorter)
            self.assertIsNotNone(shorter.short(url))