from django import forms, test
from django.core import validators
from django.db import connection
from django.db import models as django_models

import secured_fields
from main import fields, models
from secured_fields import utils
from secured_fields.enum import DatabaseVendor
from secured_fields.fernet import get_fernet
from secured_fields.mixins import EncryptedMixin


def get_field(model_class):
    return model_class._meta.get_field('field')  # pylint: disable=protected-access


class FieldInitTestCase(test.SimpleTestCase):

    def test_searchable_binary_field_not_supported(self):
        with self.assertRaises(NotImplementedError):
            secured_fields.EncryptedBinaryField(searchable=True)

    def test_searchable_default(self):
        self.assertFalse(secured_fields.EncryptedCharField(max_length=10).searchable)

    def test_unique_is_disabled(self):
        """A unique constraint on the encrypted column is meaningless since every encryption differs"""
        field = secured_fields.EncryptedCharField(max_length=10, unique=True)

        self.assertFalse(field.unique)

    def test_searchable_adds_index(self):
        field = secured_fields.EncryptedCharField(max_length=10, searchable=True)

        # MySQL does not support index on `longtext` column
        self.assertEqual(field.db_index, connection.vendor != DatabaseVendor.MYSQL)

    def test_non_searchable_has_no_index(self):
        self.assertFalse(secured_fields.EncryptedCharField(max_length=10).db_index)

    def test_non_searchable_keeps_db_index(self):
        self.assertTrue(secured_fields.EncryptedCharField(max_length=10, db_index=True).db_index)


class FieldDeconstructTestCase(test.SimpleTestCase):

    def test_non_searchable(self):
        name, path, args, kwargs = get_field(models.CharFieldModel).deconstruct()

        self.assertEqual(name, 'field')
        self.assertEqual(path, 'secured_fields.fields.EncryptedCharField')
        self.assertEqual(args, [])
        self.assertEqual(kwargs, {'max_length': 30, 'null': True})

    def test_searchable(self):
        _, _, _, kwargs = get_field(models.SearchableCharFieldModel).deconstruct()

        self.assertEqual(kwargs, {'max_length': 30, 'null': True, 'searchable': True})

    def test_unique_is_omitted(self):
        _, _, _, kwargs = secured_fields.EncryptedCharField(max_length=10, unique=True).deconstruct()

        self.assertNotIn('unique', kwargs)

    def test_non_searchable_keeps_db_index(self):
        _, _, _, kwargs = secured_fields.EncryptedCharField(max_length=10, db_index=True).deconstruct()

        self.assertIs(kwargs['db_index'], True)

    def test_reconstruct(self):
        for model_class in (models.CharFieldModel, models.SearchableCharFieldModel, models.SearchableIntegerFieldModel):
            with self.subTest(model_class=model_class):
                field = get_field(model_class)
                _, _, args, kwargs = field.deconstruct()

                reconstructed = field.__class__(*args, **kwargs)

                self.assertEqual(reconstructed.searchable, field.searchable)
                self.assertEqual(reconstructed.db_index, field.db_index)
                self.assertEqual(reconstructed.null, field.null)


class FieldInternalTypeTestCase(test.SimpleTestCase):

    def test_internal_type(self):
        cases = [
            (models.BinaryFieldModel, 'BinaryField'),
            (models.BigIntegerFieldModel, 'BigIntegerField'),
            (models.BooleanFieldModel, 'BooleanField'),
            (models.CharFieldModel, 'CharField'),
            (models.DateFieldModel, 'DateField'),
            (models.DateTimeFieldModel, 'DateTimeField'),
            (models.DecimalFieldModel, 'DecimalField'),
            (models.IntegerFieldModel, 'IntegerField'),
            (models.JSONFieldModel, 'JSONField'),
            (models.TextFieldModel, 'TextField'),
            (models.UUIDFieldModel, 'UUIDField'),
        ]

        for model_class, original_internal_type in cases:
            with self.subTest(model_class=model_class):
                field = get_field(model_class)

                # every encrypted value is stored in a text column
                self.assertEqual(field.get_internal_type(), 'TextField')
                self.assertEqual(field.get_original_internal_type(), original_internal_type)


class FieldValidatorsTestCase(test.SimpleTestCase):

    def test_integer_fields_have_same_validators_as_regular_fields(self):
        """Range validators depend on the internal type, which has to be the original one here"""
        cases = [
            (secured_fields.EncryptedIntegerField(), django_models.IntegerField()),
            (fields.EncryptedBigIntegerField(), django_models.BigIntegerField()),
        ]

        for encrypted_field, regular_field in cases:
            with self.subTest(field=encrypted_field):
                self.assertEqual(
                    [(type(validator), validator.limit_value) for validator in encrypted_field.validators],
                    [(type(validator), validator.limit_value) for validator in regular_field.validators],
                )

    def test_internal_type_is_restored(self):
        field = secured_fields.EncryptedIntegerField()

        _ = field.validators

        self.assertEqual(field.get_internal_type(), 'TextField')

    def test_char_field_has_max_length_validator(self):
        field = secured_fields.EncryptedCharField(max_length=10)

        self.assertIn(validators.MaxLengthValidator, {type(validator) for validator in field.validators})


class FieldFormFieldTestCase(test.SimpleTestCase):

    def test_form_field_class(self):
        cases = [
            (models.BooleanFieldModel, forms.BooleanField),
            (models.CharFieldModel, forms.CharField),
            (models.DateFieldModel, forms.DateField),
            (models.DateTimeFieldModel, forms.DateTimeField),
            (models.DecimalFieldModel, forms.DecimalField),
            (models.IntegerFieldModel, forms.IntegerField),
            (models.JSONFieldModel, forms.JSONField),
            (models.UUIDFieldModel, forms.UUIDField),
        ]

        for model_class, form_field_class in cases:
            with self.subTest(model_class=model_class):
                self.assertIsInstance(get_field(model_class).formfield(), form_field_class)

    def test_char_field_max_length(self):
        self.assertEqual(get_field(models.CharFieldModel).formfield().max_length, 30)


class GetEncryptedSectionTestCase(test.SimpleTestCase):

    def setUp(self):
        self.field = get_field(models.CharFieldModel)
        self.token = get_fernet().encrypt(b'test').decode()

    def test_non_searchable_value(self):
        self.assertEqual(self.field.get_encrypted_section(self.token), self.token)

    def test_searchable_value(self):
        value = self.token + EncryptedMixin.separator + utils.hash_with_salt('test')

        self.assertEqual(self.field.get_encrypted_section(value), self.token)

    def test_hashed_section_only(self):
        """A value without anything before the hashed section is not in the searchable format"""
        value = EncryptedMixin.separator + utils.hash_with_salt('test')

        self.assertEqual(self.field.get_encrypted_section(value), value)

    def test_invalid_hashed_section(self):
        for hashed_section in (
            utils.hash_with_salt('test').upper(),  # hexdigest is always lowercase
            utils.hash_with_salt('test')[:-1],  # too short
            'z' * 64,  # not hex
        ):
            with self.subTest(hashed_section=hashed_section):
                value = self.token + EncryptedMixin.separator + hashed_section

                self.assertEqual(self.field.get_encrypted_section(value), value)

    def test_wrong_separator(self):
        value = self.token + '#' + utils.hash_with_salt('test')

        self.assertEqual(self.field.get_encrypted_section(value), value)


class FromDbValueTestCase(test.SimpleTestCase):

    def test_none(self):
        self.assertIsNone(get_field(models.CharFieldModel).from_db_value(None, None, connection))

    def test_non_string_value_is_not_decrypted(self):
        """Values which are not strings cannot be encrypted, they only get converted by `to_python()`"""
        field = get_field(models.IntegerFieldModel)

        self.assertEqual(field.from_db_value(5, None, connection), 5)

    def test_decrypt(self):
        field = get_field(models.IntegerFieldModel)
        token = get_fernet().encrypt(b'5').decode()

        self.assertEqual(field.from_db_value(token, None, connection), 5)

    def test_binary_field_returns_bytes(self):
        field = get_field(models.BinaryFieldModel)
        token = get_fernet().encrypt(b'test').decode()

        self.assertEqual(field.from_db_value(token, None, connection), b'test')

    def test_invalid_token_is_returned_as_is(self):
        self.assertEqual(get_field(models.CharFieldModel).from_db_value('plain', None, connection), 'plain')


class GetDbPrepSaveTestCase(test.SimpleTestCase):

    def test_none(self):
        self.assertIsNone(get_field(models.SearchableCharFieldModel).get_db_prep_save(None, connection))

    def test_non_searchable(self):
        value = get_field(models.CharFieldModel).get_db_prep_save('test', connection)

        self.assertNotIn(EncryptedMixin.separator, value)
        self.assertEqual(get_fernet().decrypt(value.encode()), b'test')

    def test_searchable(self):
        value = get_field(models.SearchableCharFieldModel).get_db_prep_save('test', connection)

        encrypted, hashed = value.rsplit(EncryptedMixin.separator, 1)
        self.assertEqual(get_fernet().decrypt(encrypted.encode()), b'test')
        self.assertEqual(hashed, utils.hash_with_salt('test'))

    def test_encryption_is_not_deterministic(self):
        """The same value has to give a different encrypted value, while the hashed section stays the same"""
        field = get_field(models.SearchableCharFieldModel)

        first = field.get_db_prep_save('test', connection)
        second = field.get_db_prep_save('test', connection)

        self.assertNotEqual(first, second)
        self.assertEqual(first[-64:], second[-64:])

    def test_bytes_value_is_not_prepared(self):
        value = get_field(models.BinaryFieldModel).get_db_prep_save(b'\x00\xff', connection)

        self.assertEqual(get_fernet().decrypt(value.encode()), b'\x00\xff')
