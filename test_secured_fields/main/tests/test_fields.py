import datetime
import typing

import pytz
from django import test
from django.core import exceptions
from django.db import connection
from django.db.models import Model
from django.utils import timezone
from freezegun import freeze_time

from main import models
from main.tests import utils as test_utils
from secured_fields.fernet import get_fernet


class BaseTestCases:
    class BaseFieldTestCase(test.TestCase):
        model_class: typing.Type[Model]

        def setUp(self) -> None:
            self.model: typing.Optional[Model] = None

        def get_raw_field(self):
            with connection.cursor() as cursor:
                # pylint: disable=protected-access
                cursor.execute(f'SELECT field FROM {self.model_class._meta.db_table} LIMIT 1')
                result = cursor.fetchone()[0]
                return result.tobytes() if result is not None else result

        def assertIsEncryptedNone(self):
            self.assertIsNone(self.get_raw_field())

        def assertEncryptedField(self, expected_bytes: bytes):
            field_value = self.get_raw_field()
            decrypted_value = get_fernet().decrypt(field_value)

            self.assertEqual(decrypted_value, expected_bytes)

        def create_and_assert(self, create_value, assert_value: typing.Any = test_utils.NoValue, **extra_options):
            extra_options = extra_options
            if create_value is not test_utils.NoValue:
                extra_options['field'] = create_value

            self.model = self.model_class.objects.create(**extra_options)
            # self.model.refresh_from_db()

            self.assertEqual(self.model.field, assert_value if assert_value is not test_utils.NoValue else create_value)

        def test_null(self):
            model = self.model_class.objects.create(field=None)

            self.assertIsNone(model.field)
            self.assertIsEncryptedNone()


class BinaryFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.BinaryFieldModel

    def test_simple(self):
        self.create_and_assert(b'test')
        self.assertEncryptedField(b'test')


class BooleanFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.BooleanFieldModel

    def test_simple(self):
        self.create_and_assert(True)
        self.assertEncryptedField(b'True')


class CharFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.CharFieldModel

    def test_simple(self):
        self.create_and_assert('test')
        self.assertEncryptedField(b'test')

    def test_exceed_max_length(self):
        model = self.model_class(field='1234567890123456789012345678901')
        self.assertRaises(exceptions.ValidationError, model.full_clean)


class DateFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.DateFieldModel

    def test_simple(self):
        self.create_and_assert(datetime.date(2021, 12, 31))
        self.assertEncryptedField(b'2021-12-31')


class DateTimeFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.DateTimeFieldModel

    @test.override_settings(USE_TZ=False)
    def test_naive_no_use_tz(self):
        self.create_and_assert(datetime.datetime(2021, 12, 31, 23, 59, 3))
        self.assertEncryptedField(b'2021-12-31 23:59:03')

    @test.override_settings(USE_TZ=True)
    def test_naive_use_tz(self):
        self.create_and_assert(datetime.datetime(2021, 12, 31, 23, 59, 3))
        self.assertEncryptedField(b'2021-12-31 23:59:03+00:00')

    @test.override_settings(USE_TZ=True)
    def test_utc_use_tz(self):
        self.create_and_assert(datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=pytz.UTC))
        self.assertEncryptedField(b'2021-12-31 23:59:03+00:00')

    @test.override_settings(USE_TZ=True)
    def test_bangkok_use_tz(self):
        self.create_and_assert(timezone.localtime(datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=pytz.UTC)))
        self.assertEncryptedField(b'2021-12-31 23:59:03+00:00')


class IntegerFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.IntegerFieldModel

    def test_simple(self):
        model = self.model_class.objects.create(field=100)

        self.assertEqual(model.field, 100)
        self.assertEncryptedField(b'100')


class TextFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.TextFieldModel

    def test_simple(self):
        model = self.model_class.objects.create(field='test')

        self.assertEqual(model.field, 'test')
        self.assertEncryptedField(b'test')
