import os
import shutil
import tempfile

from django import test
from django.conf import settings
from django.core.files.base import ContentFile

from secured_fields.fernet import get_fernet
from secured_fields.fields.files import get_encrypted_fs
from secured_fields.storage import EncryptedFileSystemStorage


class EncryptedFileSystemStorageTestCase(test.SimpleTestCase):

    def setUp(self):
        self.location = tempfile.mkdtemp()
        self.storage = EncryptedFileSystemStorage(location=self.location)

    def tearDown(self):
        shutil.rmtree(self.location, ignore_errors=True)

    def test_save_and_open(self):
        name = self.storage.save('test.txt', ContentFile(b'test'))

        with self.storage.open(name) as f:
            self.assertEqual(f.read(), b'test')

    def test_content_is_encrypted_on_disk(self):
        name = self.storage.save('test.txt', ContentFile(b'test'))

        with open(os.path.join(self.location, name), 'rb') as f:
            raw_content = f.read()

        self.assertNotEqual(raw_content, b'test')
        self.assertEqual(get_fernet().decrypt(raw_content), b'test')

    def test_binary_content(self):
        content = bytes(range(256))
        name = self.storage.save('test.bin', ContentFile(content))

        with self.storage.open(name) as f:
            self.assertEqual(f.read(), content)

    def test_empty_content(self):
        name = self.storage.save('empty.txt', ContentFile(b''))

        with self.storage.open(name) as f:
            self.assertEqual(f.read(), b'')


class GetEncryptedFsTestCase(test.SimpleTestCase):

    def test_default(self):
        with self.settings():
            del settings.SECURED_FIELDS_FILE_STORAGE

            self.assertIsInstance(get_encrypted_fs(), EncryptedFileSystemStorage)

    @test.override_settings(SECURED_FIELDS_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_storage_without_encryption_mixin(self):
        with self.assertRaises(AssertionError):
            get_encrypted_fs()
