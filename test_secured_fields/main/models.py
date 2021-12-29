from django.db import models

import secured_fields


class BooleanFieldModel(models.Model):
    field = secured_fields.EncryptedBooleanField()


class CharFieldModel(models.Model):
    field = secured_fields.EncryptedCharField(max_length=255)


class IntegerFieldModel(models.Model):
    field = secured_fields.EncryptedIntegerField()


class TextFieldModel(models.Model):
    field = secured_fields.EncryptedTextField()
