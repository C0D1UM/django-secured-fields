import datetime
import decimal
import typing

import pytz
from django import test
from django.db import connection

from main import models
from main.tests import utils as test_utils
from secured_fields.enum import DatabaseVendor


class EncryptedExactTestCase(test.TestCase):

    def create_and_assert(self, model, create_value, assert_value: typing.Any = test_utils.NoValue):
        created_pk = model.objects.create(field=create_value).pk

        if assert_value is test_utils.NoValue:
            assert_value = create_value
        model = model.objects.filter(field=assert_value).first()

        self.assertIsNotNone(model)
        self.assertEqual(model.pk, created_pk)

    def test_boolean_field(self):
        self.create_and_assert(models.SearchableBooleanFieldModel, True)

    def test_char_field(self):
        self.create_and_assert(models.SearchableCharFieldModel, 'test')

    def test_date_field(self):
        self.create_and_assert(models.SearchableDateFieldModel, datetime.date(2021, 12, 31))

    def test_datetime_field(self):
        create_value = datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=pytz.UTC)
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
