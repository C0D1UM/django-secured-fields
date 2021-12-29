default: fix-lint lint test

lint:
	poetry run pylint secured_fields test_secured_fields

test:
	cd test_secured_fields && poetry run python manage.py test

fix-lint:
	poetry run yapf -pr secured_fields test_secured_fields
