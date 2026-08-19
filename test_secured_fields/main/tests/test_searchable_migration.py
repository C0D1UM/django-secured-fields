from django import test
from django.db import connection
from django.db.models import Model

from main import models
from secured_fields import utils
from secured_fields.fernet import get_fernet
from secured_fields.mixins import EncryptedMixin


class ChangingSearchableTestCase(test.TestCase):
    """Records saved before changing `searchable` should still be readable (issue #7)"""

    @staticmethod
    def insert_raw_value(model_class: Model, raw_value: str) -> int:
        # pylint: disable=protected-access
        with connection.cursor() as cursor:
            cursor.execute(f'INSERT INTO {model_class._meta.db_table} (field) VALUES (%s)', [raw_value])
            cursor.execute(f'SELECT MAX(id) FROM {model_class._meta.db_table}')
            return cursor.fetchone()[0]

    @staticmethod
    def get_raw_value(model_class: Model, pk: int) -> str:
        # pylint: disable=protected-access
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT field FROM {model_class._meta.db_table} WHERE id = %s', [pk])
            return cursor.fetchone()[0]

    @staticmethod
    def make_non_searchable_value(value: str) -> str:
        return get_fernet().encrypt(value.encode()).decode()

    @classmethod
    def make_searchable_value(cls, value: str) -> str:
        return cls.make_non_searchable_value(value) + EncryptedMixin.separator + utils.hash_with_salt(value)

    def test_read_non_searchable_value_with_searchable_field(self):
        """Simulate changing `searchable` from `False` to `True`"""
        pk = self.insert_raw_value(models.SearchableCharFieldModel, self.make_non_searchable_value('test'))

        model = models.SearchableCharFieldModel.objects.get(pk=pk)

        self.assertEqual(model.field, 'test')

    def test_read_searchable_value_with_non_searchable_field(self):
        """Simulate changing `searchable` from `True` to `False`"""
        pk = self.insert_raw_value(models.CharFieldModel, self.make_searchable_value('test'))

        model = models.CharFieldModel.objects.get(pk=pk)

        self.assertEqual(model.field, 'test')

    def test_resave_migrates_to_searchable(self):
        """Re-saving a record adds the hashed section, making the record searchable"""
        pk = self.insert_raw_value(models.SearchableCharFieldModel, self.make_non_searchable_value('test'))

        model = models.SearchableCharFieldModel.objects.get(pk=pk)
        model.save()

        raw_value = self.get_raw_value(models.SearchableCharFieldModel, pk)
        self.assertTrue(raw_value.endswith(EncryptedMixin.separator + utils.hash_with_salt('test')))
        self.assertEqual(models.SearchableCharFieldModel.objects.filter(field='test').count(), 1)

    def test_resave_migrates_to_non_searchable(self):
        """Re-saving a record removes the hashed section"""
        pk = self.insert_raw_value(models.CharFieldModel, self.make_searchable_value('test'))

        model = models.CharFieldModel.objects.get(pk=pk)
        model.save()

        raw_value = self.get_raw_value(models.CharFieldModel, pk)
        self.assertNotIn(EncryptedMixin.separator, raw_value)
        self.assertEqual(get_fernet().decrypt(raw_value.encode()).decode(), 'test')

    def test_to_python_keeps_token_shaped_plaintext(self):
        """In-memory values (forms, fixtures) which look like stored values must not be decrypted"""
        field = models.SearchableCharFieldModel._meta.get_field('field')  # pylint: disable=protected-access

        for plaintext in [self.make_non_searchable_value('secret'), self.make_searchable_value('secret')]:
            self.assertEqual(field.to_python(plaintext), plaintext)

    def test_unencrypted_value_with_separator_is_untouched(self):
        """A plain unencrypted value which looks like the searchable format should pass through unchanged"""
        raw_value = 'plain' + EncryptedMixin.separator + utils.hash_with_salt('plain')
        pk = self.insert_raw_value(models.CharFieldModel, raw_value)

        model = models.CharFieldModel.objects.get(pk=pk)

        self.assertEqual(model.field, raw_value)
