from cryptography.fernet import Fernet, InvalidToken

from django import test
from django.conf import settings

from main import models
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

    def test_missing_key(self):
        with self.settings():
            del settings.SECURED_FIELDS_KEY

            with self.assertRaises(AssertionError):
                get_fernet()

    def test_client_is_cached(self):
        self.assertIs(get_fernet(), get_fernet())

    def test_rotation_encrypts_with_first_key(self):
        key1 = Fernet.generate_key()
        key2 = Fernet.generate_key()

        with test.override_settings(SECURED_FIELDS_KEY=[key2, key1]):
            encrypted = get_fernet().encrypt(b'test')

        self.assertEqual(Fernet(key2).decrypt(encrypted), b'test')
        with self.assertRaises(InvalidToken):
            Fernet(key1).decrypt(encrypted)

    def test_rotation_keys_with_model(self):
        """Records encrypted with a previous key stay readable after adding a new key"""
        old_key = settings.SECURED_FIELDS_KEY
        pk = models.SearchableCharFieldModel.objects.create(field='test').pk

        fernet_module.fernet_client = None
        with test.override_settings(SECURED_FIELDS_KEY=[Fernet.generate_key().decode(), old_key]):
            self.assertEqual(models.SearchableCharFieldModel.objects.get(pk=pk).field, 'test')
            self.assertEqual(models.SearchableCharFieldModel.objects.get(field='test').pk, pk)

    def test_unknown_key_with_model(self):
        """A record encrypted with a key which is not configured cannot be decrypted"""
        pk = models.CharFieldModel.objects.create(field='test').pk

        fernet_module.fernet_client = None
        with test.override_settings(SECURED_FIELDS_KEY=Fernet.generate_key().decode()):
            self.assertNotEqual(models.CharFieldModel.objects.get(pk=pk).field, 'test')
