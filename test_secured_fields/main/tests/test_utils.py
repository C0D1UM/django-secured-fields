import hashlib

from django import test
from django.conf import settings

from secured_fields import exceptions, utils


class HashWithSaltTestCase(test.SimpleTestCase):

    @test.override_settings(SECURED_FIELDS_HASH_SALT='')
    def test_without_salt(self):
        self.assertEqual(utils.hash_with_salt('test'), hashlib.sha256(b'test').hexdigest())

    @test.override_settings(SECURED_FIELDS_HASH_SALT='salt')
    def test_with_salt(self):
        self.assertEqual(utils.hash_with_salt('test'), hashlib.sha256(b'testsalt').hexdigest())

    def test_salt_setting_is_optional(self):
        with self.settings():
            del settings.SECURED_FIELDS_HASH_SALT

            self.assertEqual(utils.hash_with_salt('test'), hashlib.sha256(b'test').hexdigest())

    @test.override_settings(SECURED_FIELDS_HASH_SALT='salt')
    def test_str_and_bytes_give_same_hash(self):
        self.assertEqual(utils.hash_with_salt('test'), utils.hash_with_salt(b'test'))

    def test_unicode(self):
        self.assertEqual(utils.hash_with_salt('สวัสดี'), utils.hash_with_salt('สวัสดี'.encode()))

    def test_different_salts_give_different_hashes(self):
        with self.settings(SECURED_FIELDS_HASH_SALT='first'):
            first = utils.hash_with_salt('test')
        with self.settings(SECURED_FIELDS_HASH_SALT='second'):
            second = utils.hash_with_salt('test')

        self.assertNotEqual(first, second)


class ExceptionsTestCase(test.SimpleTestCase):

    def test_lookup_not_supported_message(self):
        self.assertEqual(
            str(exceptions.LookupNotSupported('CharField', 'contains')),
            'Lookup `contains` for field type `CharField` is not supported.',
        )

    def test_expression_not_supported_message(self):
        message = str(exceptions.ExpressionNotSupported('CharField', 'F(field)'))

        self.assertIn("`'F(field)'`", message)
        self.assertIn('`CharField`', message)
