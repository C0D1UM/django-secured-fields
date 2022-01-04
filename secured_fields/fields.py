__all__ = [
    'EncryptedBinaryField',
    'EncryptedBooleanField',
    'EncryptedCharField',
    'EncryptedDateField',
    'EncryptedDateTimeField',
    'EncryptedDecimalField',
    'EncryptedIntegerField',
    'EncryptedJSONField',
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


class EncryptedDecimalField(mixins.EncryptedMixin, models.DecimalField):

    def get_db_prep_save(self, value, connection):
        value = super().get_db_prep_save(value, connection)
        return self.get_db_prep_value(value, connection, prepared=False)


class EncryptedIntegerField(mixins.EncryptedMixin, models.IntegerField):
    pass


class EncryptedJSONField(mixins.EncryptedMixin, models.JSONField):

    call_super_from_db_value = True


class EncryptedTextField(mixins.EncryptedMixin, models.TextField):
    pass
