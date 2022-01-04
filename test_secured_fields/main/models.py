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


class DateTimeAutoNowFieldModel(models.Model):
    field = secured_fields.EncryptedDateTimeField(auto_now=True)


class IntegerFieldModel(models.Model):
    field = secured_fields.EncryptedIntegerField(null=True)


class TextFieldModel(models.Model):
    field = secured_fields.EncryptedTextField(null=True)
