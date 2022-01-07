__all__ = [
    'EncryptedFileField',
    'EncryptedImageField',
]

from django.conf import settings
from django.db import models
from django.utils.module_loading import import_string


def get_encrypted_fs():
    fs_class_name = getattr(
        settings,
        'SECURED_FIELDS_FILE_STORAGE',
        'secured_fields.storage.EncryptedFileSystemStorage',
    )
    fs_class = import_string(fs_class_name)

    from ..mixins import EncryptedStorageMixin  # pylint: disable=import-outside-toplevel
    assert issubclass(fs_class, EncryptedStorageMixin), \
        '`SECURED_FIELDS_FILE_STORAGE` should be a subclass of `EncryptedStorageMixin`'

    return fs_class()


class EncryptedFileField(models.FileField):

    def __init__(self, *args, **kwargs):
        kwargs['storage'] = get_encrypted_fs()
        super().__init__(*args, **kwargs)


class EncryptedImageField(models.ImageField):

    def __init__(self, *args, **kwargs):
        kwargs['storage'] = get_encrypted_fs()
        super().__init__(*args, **kwargs)
