# Django Secured Fields

[![GitHub](https://img.shields.io/github/license/C0D1UM/django-secured-fields)](https://github.com/C0D1UM/django-secured-fields/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/C0D1UM/django-secured-fields/CI)](https://github.com/C0D1UM/django-secured-fields/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/C0D1UM/django-secured-fields/branch/main/graph/badge.svg?token=PN19DJ3SDF)](https://codecov.io/gh/C0D1UM/django-secured-fields)
[![PyPI](https://img.shields.io/pypi/v/django-secured-fields)](https://pypi.org/project/django-secured-fields/)  
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-secured-fields)](https://github.com/C0D1UM/django-secured-fields)
[![Django Version](https://img.shields.io/badge/django-3.1%20%7C%203.2%20%7C%204.0-blue)](https://github.com/C0D1UM/django-secured-fields)
[![PostgreSQL Version](https://img.shields.io/badge/postgres-12.9%20%7C%2013.5%20%7C%2014.1-blue)](https://github.com/C0D1UM/django-secured-fields)
[![MySQL Version](https://img.shields.io/badge/mysql-5.7%20%7C%208.0-blue)](https://github.com/C0D1UM/django-secured-fields)

Django encrypted fields with search enabled.

## Features

- Automatically encrypt/decrypt field value using [cryptography](https://github.com/pyca/cryptography)'s [Fernet](https://cryptography.io/en/latest/fernet)
- Built-in search lookup on the encrypted fields from [hashlib](https://docs.python.org/3/library/hashlib.html)'s _SHA-256_ hash value. `in` lookup also supported.
- Supports most of available Django fields including `BinaryField`, `JSONField`, and `FileField`.

## Installation

```bash
pip install django-secured-fields
```

## Setup

1. Add `secured_fields` into `INSTALLED_APPS`

   ```python
   # settings.py

   INSTALLED_APPS = [
       ...
       'secured_fields',
   ]
   ```

2. Generate a new key using for encryption

   ```bash
   $ python manage.py generate_key
   KEY: TtY8MAeXuhdKDd1HfGUwim-vQ8H7fXyRQ9J8pTi_-lg=
   HASH_SALT: 500d492e
   ```

3. Put generated key and hash salt in settings

   ```python
   # settings.py

   SECURED_FIELDS_KEY = 'TtY8MAeXuhdKDd1HfGUwim-vQ8H7fXyRQ9J8pTi_-lg='
   SECURED_FIELDS_HASH_SALT = '500d492e'  # optional
   ```

## Usage

### Simple Usage

```python
# models.py
import secured_fields

phone_number = secured_fields.EncryptedCharField(max_length=10)
```

### Enable Searching

```python
# models.py
import secured_fields

id_card_number = secured_fields.EncryptedCharField(max_length=18, searchable=True)
```

## Supported Fields

- `EncryptedBinaryField`
- `EncryptedBooleanField`
- `EncryptedCharField`
- `EncryptedDateField`
- `EncryptedDateTimeField`
- `EncryptedDecimalField`
- `EncryptedFileField`
- `EncryptedImageField`
- `EncryptedIntegerField`
- `EncryptedJSONField`
- `EncryptedTextField`

## Settings

| Key | Required | Default | Description |
| --- | -------- | ------- | ----------- |
| `SECURED_FIELDS_KEY` | Yes | | Key for using in encryption/decryption with Fernet. Usually generated from `python manage.py generate_key`. |
| `SECURED_FIELDS_HASH_SALT` | No | `''` | Salt to append after the field value before hashing. Usually generated from `python manage.py generate_key`. |
| `SECURED_FIELDS_FILE_STORAGE` | No | `'secured_fields.storage.EncryptedFileSystemStorage'` | File storage class used for storing encrypted file/image fields. See [EncryptedStorageMixin](#encryptedstoragemixin) |

## APIs

### Field Arguments

| Name | Type | Required | Default | Description |
| ---- | ---- | -------- | ------- | ----------- |
| `searchable` | `bool` | No | `False` | Enable search function |

### Encryption

```python
> from secured_fields.fernet import get_fernet

> data = b'test'

> encrypted_data = get_fernet().encrypt(data)
> encrypted_data
b'gAAAAABh2_Ry_thxLTuFFXeMc9hNttah82979JPuMSjnssRB0DmbgwdtEU5dapBgISOST_a_egDc66EG_ZtVu_EqF_69djJwuA=='

> get_fernet().decrypt(encrypted_data)
b'test'
```

### `EncryptedMixin`

If you have a field which does not supported by the package, you can use `EncryptedMixin` to enable encryption and search functionality for that custom field.

```python
import secured_fields
from django.db import models

class EncryptedUUIDField(secured_fields.EncryptedMixin, models.UUIDField):
    pass

task_id = EncryptedUUIDField(searchable=True)
```

### `EncryptedStorageMixin`

If you use a custom file storage class (e.g. defined in `settings.py`'s `DEFAULT_FILE_STORAGE`), you can enable file encryption using `EncryptedStorageMixin`.

```python
import secured_fields
from minio_storage.storage import MinioMediaStorage

class EncryptedMinioMediaStorage(
    secured_fields.EncryptedStorageMixin,
    MinioMediaStorage,
):
    pass
```

## Known Limitation

- `in` lookup on `JSONField` is not available
- Large files are not performance-friendly at the moment (see [#2](https://github.com/C0D1UM/django-secured-fields/issues/2))
- Search on `BinaryField` does not supported at the moment (see [#6](https://github.com/C0D1UM/django-secured-fields/issues/6))
- Changing `searchable` value in a field with the records in the database is not supported (see [#7](https://github.com/C0D1UM/django-secured-fields/issues/7))

## Development

### Requirements

- Docker
- Poetry
- MySQL Client
  - `brew install mysql-client`
  - `echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.bash_profile`

### Running Project

1. Start backend databases

   ```bash
   make up-db
   ```

2. Run tests (see: [Testing](#testing))

### Linting

```bash
make lint
```

### Testing

```bash
make test
```

### Fix Formatting

```bash
make yapf
```
