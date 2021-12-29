__all__ = [
    'EncryptedBooleanField',
    'EncryptedCharField',
    'EncryptedIntegerField',
    'EncryptedTextField',
]

from django.db import models

from . import mixins


class EncryptedBooleanField(mixins.EncryptedMixin, models.BooleanField):
    pass


class EncryptedCharField(mixins.EncryptedMixin, models.CharField):
    pass


class EncryptedIntegerField(mixins.EncryptedMixin, models.IntegerField):
    pass


class EncryptedTextField(mixins.EncryptedMixin, models.TextField):
    pass
