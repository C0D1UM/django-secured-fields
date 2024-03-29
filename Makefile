default: yapf lint test

lint:
	poetry run pylint secured_fields test_secured_fields

.test-pg:
	cd test_secured_fields && DATABASE_URL=postgresql://postgres:P%40ssw0rd@localhost:5432/db poetry run coverage run manage.py test

.test-mysql:
	cd test_secured_fields && DATABASE_URL=mysql://root:P%40ssw0rd@127.0.0.1:3306/db poetry run coverage run manage.py test

.test-sqlite:
	cd test_secured_fields && DATABASE_URL=sqlite:///db.sqlite3 poetry run coverage run manage.py test

.coverage-erase:
	cd test_secured_fields && poetry run coverage erase

.coverage-report:
	cd test_secured_fields && poetry run coverage report -m

test-pg: .coverage-erase .test-pg .coverage-report

test-mysql: .coverage-erase .test-mysql .coverage-report

test-sqlite: .coverage-erase .test-sqlite .coverage-report

yapf:
	poetry run yapf -ipr secured_fields test_secured_fields

migrations:
	cd test_secured_fields && poetry run python manage.py makemigrations $(filter-out $@,$(MAKECMDGOALS))

migrate:
	cd test_secured_fields && poetry run python manage.py migrate $(filter-out $@,$(MAKECMDGOALS))

shell:
	cd test_secured_fields && poetry run python manage.py shell_plus

generate-key:
	cd test_secured_fields && poetry run python manage.py generate_key

up-db:
	cd test_secured_fields && docker-compose up -d $(filter-out $@,$(MAKECMDGOALS))

down-db:
	cd test_secured_fields && docker-compose down

%:
	@:
