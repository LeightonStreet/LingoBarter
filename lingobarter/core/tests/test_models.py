# coding: utf-8
from . import BaseTestCase
from mongoengine import DoesNotExist
from lingobarter.core.models.config import Config
from lingobarter.core.models.custom_values import CustomValue


class TestConfig(BaseTestCase):
    def setUp(self):
        # Create method was not returning the created object with
        # the create() method
        try:
            self.config = Config.objects.get(group='test')
        except DoesNotExist:
            self.config = Config(group='test')
            self.config.save()

        self.config.values.append(CustomValue(name='test_config',
                                              rawvalue=u'a nice config',
                                              formatter='text'))

    def tearDown(self):
        self.config.delete()

    def test_config_fields(self):
        self.assertEqual(self.config.group, u'test')
        self.assertEqual(self.config.content_format, 'markdown')
        self.assertFalse(self.config.published)
        self.assertTrue(self.config.values.count(), 1)
        self.assertEqual(unicode(self.config), u'test')
        self.assertEqual(self.config.values[0].value, u'a nice config')

    def test_config_get(self):
        # sync the values to the database
        self.config.save()
        # then start to compare it again using get
        self.assertEqual(Config.get(group='test', name='test_config'), u'a nice config')
        self.assertEqual(Config.get(group='nonexist'), None)
        # test settings group
        self.assertIsInstance(Config.get(group='settings'), dict)
        self.assertEqual(Config.get(group='settings', name='MODE'), u'test')
