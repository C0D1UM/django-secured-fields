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
from django.utils.functional import cached_property

from . import mixins


class EncryptedBinaryField(mixins.EncryptedMixin, models.BinaryField):
    pass


class EncryptedBooleanField(mixins.EncryptedMixin, models.BooleanField):
    pass


class EncryptedCharField(mixins.EncryptedMixin, models.CharField):
    pass


class EncryptedDateField(mixins.EncryptedMixin, models.DateField):
    pass


class EncryptedDateTimeField(mixins.EncryptedMixin, models.DateTimeField):
    pass


class EncryptedIntegerField(mixins.IntegerFieldMixin, mixins.EncryptedMixin, models.IntegerField):
    pass


class EncryptedTextField(mixins.EncryptedMixin, models.TextField):
    pass
