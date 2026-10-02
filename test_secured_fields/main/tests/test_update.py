from django import test
from django.db import connection, transaction
from django.db.models import Case, F, Model, Value, When
from django.db.models.functions import Upper

from main import models
from secured_fields import utils
from secured_fields.exceptions import ExpressionNotSupported
from secured_fields.fernet import get_fernet
from secured_fields.mixins import EncryptedMixin


class UpdateTestCase(test.TestCase):
    """`update()` and `bulk_update()` pass query expressions to the field (issue #52)"""

    @staticmethod
    def get_raw_value(model_class: Model, pk: int) -> str:
        # pylint: disable=protected-access
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT field FROM {model_class._meta.db_table} WHERE id = %s', [pk])
            return cursor.fetchone()[0]

    def assert_encrypted(self, model_class: Model, pk: int, expected: str):
        raw_value = self.get_raw_value(model_class, pk)
        self.assertEqual(get_fernet().decrypt(raw_value.encode()).decode(), expected)

    def test_bulk_update(self):
        first = models.CharFieldModel.objects.create(field='first')
        second = models.CharFieldModel.objects.create(field='second')

        first.field, second.field = 'first-updated', 'second-updated'
        models.CharFieldModel.objects.bulk_update([first, second], ['field'])

        self.assertEqual(models.CharFieldModel.objects.get(pk=first.pk).field, 'first-updated')
        self.assertEqual(models.CharFieldModel.objects.get(pk=second.pk).field, 'second-updated')
        self.assert_encrypted(models.CharFieldModel, first.pk, 'first-updated')
        self.assert_encrypted(models.CharFieldModel, second.pk, 'second-updated')

    def test_bulk_update_searchable(self):
        first = models.SearchableCharFieldModel.objects.create(field='first')
        second = models.SearchableCharFieldModel.objects.create(field='second')

        first.field, second.field = 'first-updated', None
        models.SearchableCharFieldModel.objects.bulk_update([first, second], ['field'])

        raw_value = self.get_raw_value(models.SearchableCharFieldModel, first.pk)
        self.assertTrue(raw_value.endswith(EncryptedMixin.separator + utils.hash_with_salt('first-updated')))
        self.assertEqual(models.SearchableCharFieldModel.objects.get(field='first-updated').pk, first.pk)
        self.assertIsNone(self.get_raw_value(models.SearchableCharFieldModel, second.pk))

    def test_bulk_update_non_string_field(self):
        model = models.IntegerFieldModel.objects.create(field=1)

        model.field = 2
        models.IntegerFieldModel.objects.bulk_update([model], ['field'])

        self.assertEqual(models.IntegerFieldModel.objects.get(pk=model.pk).field, 2)

    def test_update_with_value(self):
        model = models.CharFieldModel.objects.create(field='test')

        models.CharFieldModel.objects.filter(pk=model.pk).update(field=Value('updated'))

        self.assertEqual(models.CharFieldModel.objects.get(pk=model.pk).field, 'updated')
        self.assert_encrypted(models.CharFieldModel, model.pk, 'updated')

    def test_update_with_value_none(self):
        model = models.CharFieldModel.objects.create(field='test')

        models.CharFieldModel.objects.filter(pk=model.pk).update(field=Value(None))

        self.assertIsNone(self.get_raw_value(models.CharFieldModel, model.pk))

    def test_update_with_unencrypted_expression(self):
        model = models.CharFieldModel.objects.create(field='test')
        queryset = models.CharFieldModel.objects.filter(pk=model.pk)

        for expression in (
            F('field'),
            Upper(Value('updated')),
            Case(When(pk=model.pk, then=Value('updated'))),
        ):
            with self.subTest(expression=expression), self.assertRaises(ExpressionNotSupported), transaction.atomic():
                queryset.update(field=expression)

        self.assert_encrypted(models.CharFieldModel, model.pk, 'test')
