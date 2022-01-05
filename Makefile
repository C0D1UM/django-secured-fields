default: fix-lint lint test

lint:
	poetry run pylint secured_fields test_secured_fields

test-pg:
	cd test_secured_fields && DATABASE_URL=postgresql://postgres:P%40ssw0rd@localhost:5432/db poetry run python manage.py test $(filter-out $@,$(MAKECMDGOALS))

test-mysql:
	cd test_secured_fields && DATABASE_URL=mysql://root:P%40ssw0rd@127.0.0.1:3306/db poetry run python manage.py test $(filter-out $@,$(MAKECMDGOALS))

yapf:
	poetry run yapf -ipr secured_fields test_secured_fields

migrations:
	cd test_secured_fields && poetry run python manage.py makemigrations $(filter-out $@,$(MAKECMDGOALS))

migrate:
	cd test_secured_fields && poetry run python manage.py migrate $(filter-out $@,$(MAKECMDGOALS))

generate-key:
	cd test_secured_fields && poetry run python manage.py generate_key

up-db:
	cd test_secured_fields && docker-compose up -d $(filter-out $@,$(MAKECMDGOALS))

down-db:
	cd test_secured_fields && docker-compose down

%:
	@:
