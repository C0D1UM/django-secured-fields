default: fix-lint lint test

lint:
	poetry run pylint secured_fields test_secured_fields

test:
	cd test_secured_fields && poetry run python manage.py test

fix-lint:
	poetry run yapf -ipr secured_fields test_secured_fields

migrations:
	cd test_secured_fields && poetry run python manage.py makemigrations $(filter-out $@,$(MAKECMDGOALS))

migrate:
	cd test_secured_fields && poetry run python manage.py migrate $(filter-out $@,$(MAKECMDGOALS))

generate-key:
	cd test_secured_fields && poetry run python manage.py generate_key

up-db:
	cd test_secured_fields && docker-compose up -d

down-db:
	cd test_secured_fields && docker-compose down

%:
	@:
