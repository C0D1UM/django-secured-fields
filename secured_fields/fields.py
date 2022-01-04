__all__ = [
    'EncryptedBinaryField',
    'EncryptedBooleanField',
    'EncryptedCharField',
    'EncryptedDateField',
    'EncryptedDateTimeField',
    'EncryptedIntegerField',
    'EncryptedTextField',
]

from django.db import models

from . import mixins


class EncryptedBinaryField(mixins.EncryptedMixin, models.BinaryField):
    def prepare_encryption(self, value) -> bytes:
        return value


class EncryptedBooleanField(mixins.EncryptedMixin, models.BooleanField):
    pass


class EncryptedCharField(mixins.EncryptedMixin, models.CharField):
    pass


class EncryptedDateField(mixins.DateMixin, mixins.EncryptedMixin, models.DateField):
    pass


class EncryptedDateTimeField(mixins.DateMixin, mixins.EncryptedMixin, models.DateTimeField):
    pass


class EncryptedIntegerField(mixins.EncryptedMixin, models.IntegerField):
    pass


class EncryptedTextField(mixins.EncryptedMixin, models.TextField):
    pass
