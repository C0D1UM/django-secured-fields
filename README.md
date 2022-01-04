# django-secured-fields

![GitHub](https://img.shields.io/github/license/C0D1UM/django-secured-fields)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/C0D1UM/django-secured-fields/CI)
![PyPI](https://img.shields.io/pypi/v/django-secured-fields)  
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-secured-fields)
![Django Version](https://img.shields.io/badge/django-3.1%20%7C%203.2-blue)
![PostgreSQL Version](https://img.shields.io/badge/postgres-12.9%20%7C%2013.5%20%7C%2014.1-blue)
![MySQL Version](https://img.shields.io/badge/mysql-5.7%20%7C%208.0-blue)

Django encrypted fields with search enabled.

# Usage

_TBD_

# Development

## Requirements

- Docker
- Poetry
- MySQL Client
  - `brew install mysql-client`
  - `echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.bash_profile`

## Running Project

### Start backend databases

```bash
make up-db
```

## Useful Commands

### Linting

```bash
make lint
```

### Testing

```bash
make test
```

### Fix Formatting

> Using `yapf`

```bash
make yapf
```
