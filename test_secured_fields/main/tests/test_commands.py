from io import StringIO
from unittest import mock

from cryptography import fernet
from django import test
from django.core.management import call_command


class GenerateKeyCommandTestCase(test.SimpleTestCase):

    def test_simple(self):
        with mock.patch('sys.stdout', new_callable=StringIO) as stdout:
            call_command('generate_key')

        key_line, hash_salt_line = stdout.getvalue().splitlines()

        # the generated key has to be usable by Fernet
        key = key_line.removeprefix('KEY: ')
        client = fernet.Fernet(key)
        self.assertEqual(client.decrypt(client.encrypt(b'test')), b'test')

        hash_salt = hash_salt_line.removeprefix('HASH_SALT: ')
        self.assertEqual(len(hash_salt), 8)
