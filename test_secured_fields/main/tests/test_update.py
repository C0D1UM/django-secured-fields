import datetime
import decimal

from django import test
from django.db import connection, transaction
from django.db.models import Case, F, Model, TextField, Value, When
from django.db.models.functions import Cast, Upper

from main import models
from main.tests import utils as test_utils
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

    def test_update_with_cast_to_field(self):
        """The shape `bulk_update()` writes on backends requiring a casted `Case` (PostgreSQL)"""
        model = models.CharFieldModel.objects.create(field='test')
        field = models.CharFieldModel._meta.get_field('field')  # pylint: disable=protected-access

        models.CharFieldModel.objects.filter(pk=model.pk).update(
            field=Cast(Case(When(pk=model.pk, then=Value('updated', output_field=field))), output_field=field)
        )

        self.assert_encrypted(models.CharFieldModel, model.pk, 'updated')

    def test_update_with_value_none(self):
        model = models.CharFieldModel.objects.create(field='test')

        models.CharFieldModel.objects.filter(pk=model.pk).update(field=Value(None))

        self.assertIsNone(self.get_raw_value(models.CharFieldModel, model.pk))

    def test_update_with_unencrypted_expression(self):
        model = models.CharFieldModel.objects.create(field='test')
        queryset = models.CharFieldModel.objects.filter(pk=model.pk)
        field = models.CharFieldModel._meta.get_field('field')  # pylint: disable=protected-access

        for expression in (
            F('field'),
            Upper(Value('updated')),
            Case(When(pk=model.pk, then=Value('updated'))),
            Cast(Value('updated', output_field=field), output_field=TextField()),
        ):
            with self.subTest(expression=expression), self.assertRaises(ExpressionNotSupported), transaction.atomic():
                queryset.update(field=expression)

        self.assert_encrypted(models.CharFieldModel, model.pk, 'test')

    def test_update_with_plain_value(self):
        model = models.CharFieldModel.objects.create(field='test')

        models.CharFieldModel.objects.filter(pk=model.pk).update(field='updated')

        self.assertEqual(models.CharFieldModel.objects.get(pk=model.pk).field, 'updated')
        self.assert_encrypted(models.CharFieldModel, model.pk, 'updated')

    def test_update_with_plain_none(self):
        model = models.CharFieldModel.objects.create(field='test')

        models.CharFieldModel.objects.filter(pk=model.pk).update(field=None)

        self.assertIsNone(self.get_raw_value(models.CharFieldModel, model.pk))

    def test_update_searchable(self):
        model = models.SearchableCharFieldModel.objects.create(field='test')

        for value in ('updated', Value('updated-again')):
            with self.subTest(value=value):
                models.SearchableCharFieldModel.objects.filter(pk=model.pk).update(field=value)

                expected = value.value if isinstance(value, Value) else value
                self.assertEqual(models.SearchableCharFieldModel.objects.get(field=expected).pk, model.pk)

        self.assertFalse(models.SearchableCharFieldModel.objects.filter(field='test').exists())

    def test_update_filtered_by_searchable_field(self):
        first = models.SearchableCharFieldModel.objects.create(field='first')
        second = models.SearchableCharFieldModel.objects.create(field='second')

        updated = models.SearchableCharFieldModel.objects.filter(field='first').update(field='updated')

        self.assertEqual(updated, 1)
        self.assertEqual(models.SearchableCharFieldModel.objects.get(pk=first.pk).field, 'updated')
        self.assertEqual(models.SearchableCharFieldModel.objects.get(pk=second.pk).field, 'second')

    def test_update_non_string_fields(self):
        cases = [
            (models.SearchableBooleanFieldModel, True, False),
            (models.SearchableDateFieldModel, datetime.date(2021, 12, 31), datetime.date(2022, 1, 1)),
            (models.SearchableDecimalFieldModel, decimal.Decimal('1.20'), decimal.Decimal('3.40')),
            (models.SearchableIntegerFieldModel, 1, 2),
            (models.SearchableJSONFieldModel, {'name': 'John'}, {'name': 'Jane'}),
            (models.SearchableUUIDFieldModel, test_utils.UUID_1, test_utils.UUID_2),
        ]

        for model_class, create_value, update_value in cases:
            with self.subTest(model_class=model_class):
                model = model_class.objects.create(field=create_value)

                model_class.objects.filter(pk=model.pk).update(field=update_value)

                self.assertEqual(model_class.objects.get(pk=model.pk).field, update_value)
                self.assertEqual(model_class.objects.get(field=update_value).pk, model.pk)

    def test_update_binary_field(self):
        model = models.BinaryFieldModel.objects.create(field=b'test')

        models.BinaryFieldModel.objects.filter(pk=model.pk).update(field=b'updated')

        self.assertEqual(bytes(models.BinaryFieldModel.objects.get(pk=model.pk).field), b'updated')

    def test_bulk_update_non_string_fields(self):
        cases = [
            (models.SearchableBooleanFieldModel, True, False),
            (models.SearchableDateFieldModel, datetime.date(2021, 12, 31), datetime.date(2022, 1, 1)),
            (models.SearchableDecimalFieldModel, decimal.Decimal('1.20'), decimal.Decimal('3.40')),
            (models.SearchableJSONFieldModel, {'name': 'John'}, {'name': 'Jane'}),
            (models.SearchableUUIDFieldModel, test_utils.UUID_1, test_utils.UUID_2),
        ]

        for model_class, create_value, update_value in cases:
            with self.subTest(model_class=model_class):
                model = model_class.objects.create(field=create_value)

                model.field = update_value
                model_class.objects.bulk_update([model], ['field'])

                self.assertEqual(model_class.objects.get(pk=model.pk).field, update_value)
                self.assertEqual(model_class.objects.get(field=update_value).pk, model.pk)

    def test_bulk_update_binary_field(self):
        model = models.BinaryFieldModel.objects.create(field=b'test')

        model.field = b'updated'
        models.BinaryFieldModel.objects.bulk_update([model], ['field'])

        self.assertEqual(bytes(models.BinaryFieldModel.objects.get(pk=model.pk).field), b'updated')

    def test_bulk_update_with_batch_size(self):
        instances = [models.SearchableCharFieldModel.objects.create(field=f'value-{i}') for i in range(5)]

        for instance in instances:
            instance.field += '-updated'
        models.SearchableCharFieldModel.objects.bulk_update(instances, ['field'], batch_size=2)

        for instance in instances:
            self.assertEqual(models.SearchableCharFieldModel.objects.get(field=instance.field).pk, instance.pk)

    def test_bulk_create(self):
        created = models.SearchableCharFieldModel.objects.bulk_create([
            models.SearchableCharFieldModel(field='first'),
            models.SearchableCharFieldModel(field='second'),
        ])

        self.assertEqual(len(created), 2)
        self.assertEqual(models.SearchableCharFieldModel.objects.filter(field__in=['first', 'second']).count(), 2)
        for value in ('first', 'second'):
            pk = models.SearchableCharFieldModel.objects.get(field=value).pk
            raw_value = self.get_raw_value(models.SearchableCharFieldModel, pk)
            self.assertTrue(raw_value.endswith(EncryptedMixin.separator + utils.hash_with_salt(value)))

    def test_update_or_create(self):
        model = models.SearchableCharFieldModel.objects.create(field='test')

        updated, created = models.SearchableCharFieldModel.objects.update_or_create(
            field='test', defaults={'field': 'updated'}
        )

        self.assertFalse(created)
        self.assertEqual(updated.pk, model.pk)
        self.assertEqual(models.SearchableCharFieldModel.objects.get(pk=model.pk).field, 'updated')

    def test_update_with_case_default_none(self):
        """A `Case` resolving to encrypted values or `None` is accepted"""
        model = models.CharFieldModel.objects.create(field='test')
        other = models.CharFieldModel.objects.create(field='other')
        field = models.CharFieldModel._meta.get_field('field')  # pylint: disable=protected-access

        models.CharFieldModel.objects.update(
            field=Case(When(pk=model.pk, then=Value('updated', output_field=field)), default=Value(None))
        )

        self.assert_encrypted(models.CharFieldModel, model.pk, 'updated')
        self.assertIsNone(self.get_raw_value(models.CharFieldModel, other.pk))

    def test_update_with_unencrypted_expression_on_other_fields(self):
        for model_class in (models.IntegerFieldModel, models.SearchableIntegerFieldModel, models.JSONFieldModel):
            with self.subTest(model_class=model_class), self.assertRaises(ExpressionNotSupported), \
                    transaction.atomic():
                model_class.objects.update(field=F('field'))

    def test_save_updates_value(self):
        model = models.SearchableCharFieldModel.objects.create(field='test')

        model.field = 'updated'
        model.save(update_fields=['field'])

        self.assertEqual(models.SearchableCharFieldModel.objects.get(field='updated').pk, model.pk)
        self.assertFalse(models.SearchableCharFieldModel.objects.filter(field='test').exists())
