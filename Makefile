default: fix-lint lint test

lint:
	poetry run pylint secured_fields test_secured_fields

test:
	cd test_secured_fields && poetry run python manage.py test

fix-lint:
	poetry run yapf -ipr secured_fields test_secured_fields

migrations-migrate:
	cd test_secured_fields && poetry run python manage.py makemigrations
	cd test_secured_fields && poetry run python manage.py migrate

generate-key:
	cd test_secured_fields && poetry run python manage.py generate_key
