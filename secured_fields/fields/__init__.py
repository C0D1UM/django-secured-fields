__all__ = [
    'EncryptedBinaryField',
    'EncryptedBooleanField',
    'EncryptedCharField',
    'EncryptedDateField',
    'EncryptedDateTimeField',
    'EncryptedDecimalField',
    'EncryptedFileField',
    'EncryptedImageField',
    'EncryptedIntegerField',
    'EncryptedJSONField',
    'EncryptedTextField',
]

from django.db import models

from .files import *
from .. import mixins


class EncryptedBinaryField(mixins.EncryptedMixin, models.BinaryField):

    def prepare_encryption(self, value) -> bytes:
        return value


class EncryptedBooleanField(mixins.EncryptedMixin, models.BooleanField):

    # prevent lint error
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EncryptedCharField(mixins.EncryptedMixin, models.CharField):
    pass


class EncryptedDateField(mixins.EncryptedMixin, models.DateField):
    pass


class EncryptedDateTimeField(mixins.EncryptedMixin, models.DateTimeField):
    pass


class EncryptedDecimalField(mixins.EncryptedMixin, models.DecimalField):
    pass


class EncryptedIntegerField(mixins.EncryptedMixin, models.IntegerField):

    # prevent lint error
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EncryptedJSONField(mixins.EncryptedMixin, models.JSONField):
    call_super_from_db_value = True


class EncryptedTextField(mixins.EncryptedMixin, models.TextField):
    pass
