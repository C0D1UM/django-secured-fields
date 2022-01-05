import base64
import datetime
import decimal
import typing
import warnings

import pytz
from django import test
from django.core import exceptions
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.models import Model
from django.utils import timezone
from freezegun import freeze_time

import secured_fields
from main import models
from main.tests import utils as test_utils
from secured_fields.enum import DatabaseVendor
from secured_fields.exceptions import DatabaseBackendNotSupported
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

                # postgres support
                if isinstance(result, memoryview) and result is not None:
                    result = result.tobytes()

                return result

        def assert_is_encrypted_none(self):
            self.assertIsNone(self.get_raw_field())

        def assert_encrypted_field(self, expected_bytes: bytes):
            field_value = self.get_raw_field()
            decrypted_value = get_fernet().decrypt(field_value)

            self.assertEqual(decrypted_value, expected_bytes)

        def create_and_assert(self, create_value, assert_value: typing.Any = test_utils.NoValue, **extra_options):
            if create_value is not test_utils.NoValue:
                extra_options['field'] = create_value

            self.model = self.model_class.objects.create(**extra_options)
            self.model.refresh_from_db()

            self.assertEqual(self.model.field, assert_value if assert_value is not test_utils.NoValue else create_value)

    class NullValueTestMixin(object):

        def test_null(self):
            self.create_and_assert(None)
            self.assert_is_encrypted_none()

    class BaseFileFieldTestCase(test_utils.FileTestMixin, BaseFieldTestCase):
        file_name: str
        file_content: bytes

        def setUp(self) -> None:
            self.uploaded_file = SimpleUploadedFile(self.file_name, self.file_content)


class BinaryFieldTestCase(BaseTestCases.NullValueTestMixin, BaseTestCases.BaseFieldTestCase):
    model_class = models.BinaryFieldModel

    def test_simple(self):
        self.create_and_assert(b'test')
        self.assert_encrypted_field(b'test')


class BooleanFieldTestCase(BaseTestCases.NullValueTestMixin, BaseTestCases.BaseFieldTestCase):
    model_class = models.BooleanFieldModel

    def test_simple(self):
        self.create_and_assert(True)
        self.assert_encrypted_field(b'True')


class CharFieldTestCase(BaseTestCases.NullValueTestMixin, BaseTestCases.BaseFieldTestCase):
    model_class = models.CharFieldModel

    def test_simple(self):
        self.create_and_assert('test')
        self.assert_encrypted_field(b'test')

    def test_exceed_max_length(self):
        # TODO: enforce validation
        model = self.model_class(field='1234567890123456789012345678901')
        self.assertRaises(exceptions.ValidationError, model.full_clean)


class DateFieldTestCase(BaseTestCases.NullValueTestMixin, BaseTestCases.BaseFieldTestCase):
    model_class = models.DateFieldModel

    def test_simple(self):
        self.create_and_assert(datetime.date(2021, 12, 31))
        self.assert_encrypted_field(b'2021-12-31')


@freeze_time(datetime.datetime(2021, 12, 31))
class DateFieldWithAutoNowTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.DateFieldAutoNowModel

    def test_simple(self):
        self.create_and_assert(test_utils.NoValue, datetime.date(2021, 12, 31))
        self.assert_encrypted_field(b'2021-12-31')


class DateTimeFieldTestCase(BaseTestCases.NullValueTestMixin, BaseTestCases.BaseFieldTestCase):
    model_class = models.DateTimeFieldModel

    @test.override_settings(USE_TZ=False)
    def test_naive_no_use_tz(self):
        self.create_and_assert(datetime.datetime(2021, 12, 31, 23, 59, 3))
        self.assert_encrypted_field(b'2021-12-31 23:59:03')

    @test.override_settings(USE_TZ=True)
    def test_naive_use_tz(self):
        warnings.simplefilter('ignore', RuntimeWarning)

        create_value = datetime.datetime(2021, 12, 31, 23, 59, 3)

        if connection.vendor == DatabaseVendor.POSTGRESQL:
            self.create_and_assert(create_value, datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=pytz.UTC))
            self.assert_encrypted_field(b'2021-12-31 23:59:03+00:00')
        elif connection.vendor == DatabaseVendor.MYSQL:
            # mysql is timezone naive
            self.create_and_assert(create_value, datetime.datetime(2021, 12, 31, 23, 59, 3))
            self.assert_encrypted_field(b'2021-12-31 23:59:03')
        else:
            raise DatabaseBackendNotSupported

    @test.override_settings(USE_TZ=True)
    def test_utc_use_tz(self):
        create_value = timezone.make_aware(datetime.datetime(2021, 12, 31, 23, 59, 3), pytz.UTC)

        if connection.vendor == DatabaseVendor.POSTGRESQL:
            self.create_and_assert(create_value, assert_value=create_value)
            self.assert_encrypted_field(b'2021-12-31 23:59:03+00:00')
        elif connection.vendor == DatabaseVendor.MYSQL:
            # mysql is timezone naive
            self.create_and_assert(create_value, datetime.datetime(2021, 12, 31, 23, 59, 3))
            self.assert_encrypted_field(b'2021-12-31 23:59:03')
        else:
            raise DatabaseBackendNotSupported

    @test.override_settings(USE_TZ=True)
    def test_bangkok_use_tz(self):
        create_value = timezone.make_aware(datetime.datetime(2021, 12, 31, 23, 59, 3), pytz.timezone('Asia/Bangkok'))

        if connection.vendor == DatabaseVendor.POSTGRESQL:
            self.create_and_assert(create_value, assert_value=create_value)
            self.assert_encrypted_field(b'2021-12-31 23:59:03+07:00')
        elif connection.vendor == DatabaseVendor.MYSQL:
            # mysql is timezone naive
            self.create_and_assert(create_value, datetime.datetime(2021, 12, 31, 16, 59, 3))
            self.assert_encrypted_field(b'2021-12-31 16:59:03')
        else:
            raise DatabaseBackendNotSupported


@freeze_time(datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=pytz.UTC))
@test.override_settings(USE_TZ=True)
class DateTimeFieldWithAutoNowTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.DateTimeFieldAutoNowModel

    def test_simple(self):
        create_value = datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=pytz.UTC)

        if connection.vendor == DatabaseVendor.POSTGRESQL:
            self.create_and_assert(create_value, assert_value=create_value)
            self.assert_encrypted_field(b'2021-12-31 23:59:03+00:00')
        elif connection.vendor == DatabaseVendor.MYSQL:
            # mysql is timezone naive
            self.create_and_assert(create_value, datetime.datetime(2021, 12, 31, 23, 59, 3))
            self.assert_encrypted_field(b'2021-12-31 23:59:03')
        else:
            raise DatabaseBackendNotSupported


class DecimalFieldTestCase(BaseTestCases.NullValueTestMixin, BaseTestCases.BaseFieldTestCase):
    model_class = models.DecimalFieldModel

    def test_simple(self):
        self.create_and_assert(decimal.Decimal('100.23'))
        self.assert_encrypted_field(b'100.23')


class CustomEncryptedFileStorage(secured_fields.EncryptedStorageMixin, FileSystemStorage):
    pass


class FileFieldTestCase(BaseTestCases.BaseFileFieldTestCase):
    model_class = models.FileFieldModel
    file_name = 'test.txt'
    file_content = b'test'

    def _test(self):
        model = self.model_class.objects.create(field=self.uploaded_file)
        model.refresh_from_db()

        self.assertTrue(model.field)
        self.assertEqual(model.field.name, self.file_name)
        self.assertEqual(model.field.read(), self.file_content)
        with open(model.field.path, 'rb') as f:
            self.assertEqual(get_fernet().decrypt(f.read()), self.file_content)

    def test_simple(self):
        self._test()

    def test_null(self):
        model = self.model_class.objects.create(field=None)
        model.refresh_from_db()

        self.assertFalse(model.field)

    @test.override_settings(ENCRYPTED_FILE_STORAGE='main.tests.test_fields.CustomEncryptedFileStorage')
    def test_custom_fs_class(self):
        self._test()


class FileFieldNoEncryptionTestCase(BaseTestCases.BaseFileFieldTestCase):
    model_class = models.FileFieldNoEncryptionModel
    file_name = 'test.txt'
    file_content = b'test'

    def test_simple(self):
        model = self.model_class.objects.create(field=self.uploaded_file)
        model.refresh_from_db()

        self.assertTrue(model.field)
        self.assertEqual(model.field.name, self.file_name)
        self.assertEqual(model.field.read(), self.file_content)
        with open(model.field.path, 'rb') as f:
            self.assertEqual(f.read(), self.file_content)


class ImageFieldTestCase(FileFieldTestCase):
    model_class = models.ImageFieldModel
    file_name = 'test.png'
    file_content = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
    )


class IntegerFieldTestCase(BaseTestCases.NullValueTestMixin, BaseTestCases.BaseFieldTestCase):
    model_class = models.IntegerFieldModel

    def test_simple(self):
        self.create_and_assert(100)
        self.assert_encrypted_field(b'100')


class JSONFieldTestCase(BaseTestCases.NullValueTestMixin, BaseTestCases.BaseFieldTestCase):
    model_class = models.JSONFieldModel

    def test_simple(self):
        self.create_and_assert({'name': 'John Doe'})
        self.assert_encrypted_field(b'{"name": "John Doe"}')


class TextFieldTestCase(BaseTestCases.NullValueTestMixin, BaseTestCases.BaseFieldTestCase):
    model_class = models.TextFieldModel

    def test_simple(self):
        self.create_and_assert('test')
        self.assert_encrypted_field(b'test')
