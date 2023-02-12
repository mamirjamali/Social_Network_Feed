"""
Test custom management commands.
"""
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error


@patch('core.management.commands.wait_for_db.Command.check')
class CommandsTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test if database ready"""
        patched_check.retrun_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test if database get operationalErro"""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 4 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 7)
        patched_check.assert_called_with(databases=['default'])
