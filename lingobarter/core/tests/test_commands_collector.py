from mock import patch
from lingobarter.core.tests import BaseTestCase
from lingobarter.ext.commands_collector import CommandsCollector


class TestCommandsCollector(BaseTestCase):

    @patch('lingobarter.ext.commands_collector.os.walk')
    @patch('lingobarter.ext.commands_collector.os.listdir')
    @patch('lingobarter.ext.commands_collector.importlib.import_module')
    def test_load_commands(self, m_import_module, m_listdir, m_walk):
        m_walk.return_value = [('px', ['commands', 'aaa'], 'aa')]
        m_listdir.return_value = [
            'testx.py', 'cmd_blah', '__init__.py', 'xyz.py']
        cmd = CommandsCollector('my_path', 'my_module')
        self.assertListEqual(
            ['px_testx', 'px_xyz'], cmd.list_commands(cmd))
        cmd.get_command(cmd, 'px_testx')
        m_import_module.assert_called_once_with(
            'my_module.px.commands.testx')
