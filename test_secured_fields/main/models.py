from django.db import models

import secured_fields


class BooleanFieldModel(models.Model):
    field = secured_fields.EncryptedBooleanField(null=True)


class CharFieldModel(models.Model):
    field = secured_fields.EncryptedCharField(max_length=255, null=True)


class IntegerFieldModel(models.Model):
    field = secured_fields.EncryptedIntegerField(null=True)


class TextFieldModel(models.Model):
    field = secured_fields.EncryptedTextField(null=True)
