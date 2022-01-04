from django.core.files.storage import FileSystemStorage
from django.db import models

import secured_fields


class BinaryFieldModel(models.Model):
    field = secured_fields.EncryptedBinaryField(null=True)


class BooleanFieldModel(models.Model):
    field = secured_fields.EncryptedBooleanField(null=True)


class CharFieldModel(models.Model):
    field = secured_fields.EncryptedCharField(max_length=30, null=True)


class DateFieldModel(models.Model):
    field = secured_fields.EncryptedDateField(null=True)


class DateFieldAutoNowModel(models.Model):
    field = secured_fields.EncryptedDateField(auto_now=True)


class DateTimeFieldModel(models.Model):
    field = secured_fields.EncryptedDateTimeField(null=True)


class DateTimeFieldAutoNowModel(models.Model):
    field = secured_fields.EncryptedDateTimeField(auto_now=True)


class DecimalFieldModel(models.Model):
    field = secured_fields.EncryptedDecimalField(max_digits=6, decimal_places=2, null=True)


class DateTimeAutoNowFieldModel(models.Model):
    field = secured_fields.EncryptedDateTimeField(auto_now=True)


class FileFieldModel(models.Model):
    field = secured_fields.EncryptedFileField(null=True)


class FileFieldNoEncryptionModel(models.Model):
    field = models.FileField()


class FileFieldCustomEncryptionModel(models.Model):
    class CustomEncryptedFileStorage(secured_fields.EncryptedStorageMixin, FileSystemStorage):
        pass

    field = models.FileField(storage=CustomEncryptedFileStorage(), null=True)


class ImageFieldModel(models.Model):
    field = secured_fields.EncryptedImageField(null=True)


class IntegerFieldModel(models.Model):
    field = secured_fields.EncryptedIntegerField(null=True)


class JSONFieldModel(models.Model):
    field = secured_fields.EncryptedJSONField(null=True)


class TextFieldModel(models.Model):
    field = secured_fields.EncryptedTextField(null=True)
