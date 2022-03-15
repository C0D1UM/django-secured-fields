import datetime
import decimal
import typing

from django import test
from django.db import connection

from main import models
from main.tests import utils as test_utils
from secured_fields import exceptions
from secured_fields.enum import DatabaseVendor


@test.override_settings(SECURED_FIELDS_HASH_SALT='test')
class EncryptedExactLookupTestCase(test.TestCase):

    def create_and_assert(self, model, create_value, assert_value: typing.Any = test_utils.NoValue):
        created_pk = model.objects.create(field=create_value).pk

        if assert_value is test_utils.NoValue:
            assert_value = create_value
        model = model.objects.filter(field=assert_value).first()

        self.assertIsNotNone(model)
        self.assertEqual(model.pk, created_pk)

    def assert_no_lookup(self, model, assert_value: typing.Any):
        self.assertRaises(exceptions.LookupNotSupported, model.objects.filter, field=assert_value)

    def test_binary_field(self):
        self.assert_no_lookup(models.BinaryFieldModel, b'test')

    def test_boolean_field(self):
        self.create_and_assert(models.SearchableBooleanFieldModel, True)

    def test_char_field(self):
        self.create_and_assert(models.SearchableCharFieldModel, 'test')

    def test_date_field(self):
        self.create_and_assert(models.SearchableDateFieldModel, datetime.date(2021, 12, 31))

    def test_datetime_field(self):
        create_value = datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=test_utils.TZ_UTC)
        assert_value = create_value

        if connection.vendor == DatabaseVendor.MYSQL:
            # mysql is timezone naive
            assert_value = assert_value.replace(tzinfo=None)

        self.create_and_assert(models.SearchableDateTimeFieldModel, create_value, assert_value)

    def test_decimal_field(self):
        self.create_and_assert(models.SearchableDecimalFieldModel, decimal.Decimal('100.23'))

    def test_integer_field(self):
        self.create_and_assert(models.SearchableIntegerFieldModel, 100)

    def test_json_field(self):
        self.create_and_assert(models.SearchableJSONFieldModel, {'name': 'John Doe'})

    def test_text_field(self):
        self.create_and_assert(models.SearchableTextFieldModel, 'test')


@test.override_settings(SECURED_FIELDS_HASH_SALT='test')
class EncryptedInLookupTestCase(test.TestCase):

    def create_and_assert(self, model, create_value, assert_value):
        created_pk = model.objects.create(field=create_value).pk

        if not isinstance(assert_value, list):
            assert_value = [assert_value]
        model = model.objects.filter(field__in=assert_value).first()

        self.assertIsNotNone(model)
        self.assertEqual(model.pk, created_pk)

    def assert_no_lookup(self, model, assert_value: typing.Any):
        self.assertRaises(exceptions.LookupNotSupported, model.objects.filter, field__in=assert_value)

    def test_binary_field(self):
        self.assert_no_lookup(models.BinaryFieldModel, b'test')

    def test_boolean_field(self):
        self.create_and_assert(models.SearchableBooleanFieldModel, True, [True, False])

    def test_char_field(self):
        self.create_and_assert(models.SearchableCharFieldModel, 'test', ['test', 'user'])

    def test_date_field(self):
        self.create_and_assert(
            models.SearchableDateFieldModel,
            datetime.date(2021, 12, 31),
            [datetime.date(2021, 12, 31), datetime.date(2022, 2, 1)],
        )

    def test_datetime_field(self):
        create_value = datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=test_utils.TZ_UTC)
        assert_value = [
            datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=test_utils.TZ_UTC),
            datetime.datetime(2021, 12, 31, 23, 50, 3, tzinfo=test_utils.TZ_UTC),
        ]

        if connection.vendor == DatabaseVendor.MYSQL:
            # mysql is timezone naive
            assert_value = list(map(lambda x: x.replace(tzinfo=None), assert_value))

        self.create_and_assert(models.SearchableDateTimeFieldModel, create_value, assert_value)

    def test_decimal_field(self):
        self.create_and_assert(
            models.SearchableDecimalFieldModel,
            decimal.Decimal('100.23'),
            [decimal.Decimal('100.23'), decimal.Decimal('10.2')],
        )

    def test_integer_field(self):
        self.create_and_assert(models.SearchableIntegerFieldModel, 100, [100, 200])

    def test_json_field(self):
        self.assert_no_lookup(models.SearchableJSONFieldModel, [{'test': 'test'}, {'john': 'doe'}])

    def test_text_field(self):
        self.create_and_assert(models.SearchableTextFieldModel, 'test', ['test', 'user'])


@test.override_settings(SECURED_FIELDS_HASH_SALT='test')
class IsNullLookupTestCase(test.TestCase):

    def create_and_assert(self, model):
        created_pk = model.objects.create(field=None).pk
        model = model.objects.filter(field__isnull=True).first()

        self.assertIsNotNone(model)
        self.assertEqual(model.pk, created_pk)

    def test_binary_field(self):
        self.create_and_assert(models.BinaryFieldModel)

    def test_boolean_field(self):
        self.create_and_assert(models.SearchableBooleanFieldModel)

    def test_char_field(self):
        self.create_and_assert(models.SearchableCharFieldModel)

    def test_date_field(self):
        self.create_and_assert(models.SearchableDateFieldModel)

    def test_datetime_field(self):
        self.create_and_assert(models.SearchableDateTimeFieldModel)

    def test_decimal_field(self):
        self.create_and_assert(models.SearchableDecimalFieldModel)

    def test_integer_field(self):
        self.create_and_assert(models.SearchableIntegerFieldModel)

    def test_json_field(self):
        self.create_and_assert(models.SearchableJSONFieldModel)

    def test_text_field(self):
        self.create_and_assert(models.SearchableTextFieldModel)


class UnsupportedLookupTestCase(test.TestCase):

    def test_char_field_contains(self):
        self.assertRaises(
            exceptions.LookupNotSupported,
            models.SearchableCharFieldModel.objects.filter,
            field__contains='test',
        )
