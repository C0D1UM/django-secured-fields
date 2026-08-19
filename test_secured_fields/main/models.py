from django.db import models

import secured_fields
from main import fields


class BinaryFieldModel(models.Model):
    field = secured_fields.EncryptedBinaryField(null=True)


class BigIntegerFieldModel(models.Model):
    field = fields.EncryptedBigIntegerField(null=True)


class SearchableBigIntegerFieldModel(models.Model):
    field = fields.EncryptedBigIntegerField(null=True, searchable=True)


class BooleanFieldModel(models.Model):
    field = secured_fields.EncryptedBooleanField(null=True)


class SearchableBooleanFieldModel(models.Model):
    field = secured_fields.EncryptedBooleanField(null=True, searchable=True)  # pylint: disable=unexpected-keyword-arg


class CharFieldModel(models.Model):
    field = secured_fields.EncryptedCharField(max_length=30, null=True)


class SearchableCharFieldModel(models.Model):
    field = secured_fields.EncryptedCharField(max_length=30, null=True, searchable=True)


class DateFieldModel(models.Model):
    field = secured_fields.EncryptedDateField(null=True)


class DateFieldAutoNowModel(models.Model):
    field = secured_fields.EncryptedDateField(auto_now=True)


class SearchableDateFieldModel(models.Model):
    field = secured_fields.EncryptedDateField(null=True, searchable=True)


class DateTimeFieldModel(models.Model):
    field = secured_fields.EncryptedDateTimeField(null=True)


class DateTimeFieldAutoNowModel(models.Model):
    field = secured_fields.EncryptedDateTimeField(auto_now=True)


class SearchableDateTimeFieldModel(models.Model):
    field = secured_fields.EncryptedDateTimeField(null=True, searchable=True)


class DecimalFieldModel(models.Model):
    field = secured_fields.EncryptedDecimalField(max_digits=6, decimal_places=2, null=True)


class SearchableDecimalFieldModel(models.Model):
    field = secured_fields.EncryptedDecimalField(max_digits=6, decimal_places=2, null=True, searchable=True)


class FileFieldModel(models.Model):
    field = secured_fields.EncryptedFileField(null=True)


class FileFieldNoEncryptionModel(models.Model):
    field = models.FileField()


class ImageFieldModel(models.Model):
    field = secured_fields.EncryptedImageField(null=True)


class IntegerFieldModel(models.Model):
    field = secured_fields.EncryptedIntegerField(null=True)


class SearchableIntegerFieldModel(models.Model):
    field = secured_fields.EncryptedIntegerField(null=True, searchable=True)  # pylint: disable=unexpected-keyword-arg


class JSONFieldModel(models.Model):
    field = secured_fields.EncryptedJSONField(null=True)


class SearchableJSONFieldModel(models.Model):
    field = secured_fields.EncryptedJSONField(null=True, searchable=True)


class TextFieldModel(models.Model):
    field = secured_fields.EncryptedTextField(null=True)


class SearchableTextFieldModel(models.Model):
    field = secured_fields.EncryptedTextField(null=True, searchable=True)


class UUIDFieldModel(models.Model):
    field = fields.EncryptedUUIDField(null=True)


class SearchableUUIDFieldModel(models.Model):
    field = fields.EncryptedUUIDField(null=True, searchable=True)
