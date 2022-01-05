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

    # def get_db_prep_value(self, value, connection, prepared=False):
    #     if prepared:
    #         value = super().get_prep_value(value)
    #     return super().get_db_prep_value(value, connection, prepared)


class EncryptedBooleanField(mixins.EncryptedMixin, models.BooleanField):
    pass


class EncryptedCharField(mixins.EncryptedMixin, models.CharField):
    pass


class EncryptedDateField(mixins.EncryptedMixin, models.DateField):
    pass


class EncryptedDateTimeField(mixins.EncryptedMixin, models.DateTimeField):
    pass


class EncryptedDecimalField(mixins.EncryptedMixin, models.DecimalField):
    pass

    # def get_db_prep_save(self, value, connection):
    #     value = super().get_db_prep_save(value, connection)
    #     return self.get_db_prep_value(value, connection, prepared=False)


class EncryptedIntegerField(mixins.EncryptedMixin, models.IntegerField):
    pass


class EncryptedJSONField(mixins.EncryptedMixin, models.JSONField):
    call_super_from_db_value = True


class EncryptedTextField(mixins.EncryptedMixin, models.TextField):
    pass
