from cryptography.fernet import Fernet

from django import test

from secured_fields import fernet as fernet_module
from secured_fields.fernet import get_fernet


class FernetTestCase(test.TestCase):
    def setUp(self):
        fernet_module.fernet_client = None

    def tearDown(self) -> None:
        fernet_module.fernet_client = None

    def test_simple(self):
        fernet = get_fernet()
        encrypted = fernet.encrypt(b'test')
        self.assertEqual(fernet.decrypt(encrypted), b'test')

    def test_rotation_keys(self):
        key1 = Fernet.generate_key()
        fernet = Fernet(key1)
        encrypted = fernet.encrypt(b'test')
        self.assertEqual(fernet.decrypt(encrypted), b'test')

        key2 = Fernet.generate_key()
        with test.override_settings(SECURED_FIELDS_KEY=[key2, key1]):
            fernet = get_fernet()
            self.assertEqual(fernet.decrypt(encrypted), b'test')

            encrypted_2 = fernet.encrypt(b'test')
            self.assertEqual(fernet.decrypt(encrypted_2), b'test')
