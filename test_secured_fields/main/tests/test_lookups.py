import datetime
import decimal

import pytz
from django import test

from main import models


class EncryptedExactTestCase(test.TestCase):

    def create_and_assert(self, model, value):
        created_pk = model.objects.create(field=value).pk
        model = model.objects.filter(field=value).first()

        self.assertIsNotNone(model)
        self.assertEqual(model.pk, created_pk)

    def test_boolean_field(self):
        self.create_and_assert(models.SearchableBooleanFieldModel, True)

    def test_char_field(self):
        self.create_and_assert(models.SearchableCharFieldModel, 'test')

    def test_date_field(self):
        self.create_and_assert(models.SearchableDateFieldModel, datetime.date(2021, 12, 31))

    def test_datetime_field(self):
        self.create_and_assert(
            models.SearchableDateTimeFieldModel,
            datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=pytz.UTC),
        )

    def test_decimal_field(self):
        self.create_and_assert(models.SearchableDecimalFieldModel, decimal.Decimal('100.23'))

    def test_integer_field(self):
        self.create_and_assert(models.SearchableIntegerFieldModel, 100)

    def test_json_field(self):
        self.create_and_assert(models.SearchableJSONFieldModel, {'name': 'John Doe'})

    def test_text_field(self):
        self.create_and_assert(models.SearchableTextFieldModel, 'test')
