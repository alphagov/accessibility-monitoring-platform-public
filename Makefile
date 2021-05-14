init:
	pip install --upgrade pip \
		&& pip install pipenv \
		&& pipenv install -d \
		&& npm i \
		&& npm install --only=dev \
		&& npm link gulp \
		&& gulp build \
		&& docker-compose up -d \
		&& sleep 20 \
		&& psql postgres://admin:secret@localhost:5432/postgres -c "create database accessibility_monitoring_app;" \
		&& psql postgres://admin:secret@localhost:5432/postgres -c "create database a11ymon;" \
		&& echo "password is secret" \
		&& pg_restore --no-privileges --no-owner -h localhost -p 5432 -U admin -d a11ymon -1 ./data/pubsecweb_210216.pgadmin-backup \
		&& pg_restore --no-privileges --no-owner -h localhost -p 5432 -U admin -d a11ymon -1 ./data/a11ymon210408.pgadmin-backup \
		&& ./manage.py migrate query_local_website_registry --database=pubsecweb_db \
		&& ./manage.py migrate \
		&& python3 manage.py loaddata ./data/auth_data.json \
		&& psql -Atx postgres://admin:secret@localhost:5432/a11ymon -c "\COPY pubsecweb.nuts_conversion FROM './data/Local_Authority_District_(December_2018)_to_NUTS3_to_NUTS2_to_NUTS1_(January_2018)_Lookup_in_United_Kingdom.csv' DELIMITER ',' CSV HEADER;" \
		&& echo "email is admin@email.com and password is secret"

start:
	python manage.py runserver 8081

sync:
	gulp serve

mail_server:
	python -m smtpd -n -c DebuggingServer localhost:1025

test:
	coverage run --source='.' manage.py test && coverage report --skip-covered && coverage erase

lighthouse_audit:
	node lighthouse-tests/lighthouse-test.js

load_data:
	python3 manage.py loaddata $(value db_data)

local_deploy:
	pipenv lock -r > requirements.txt
	cf push -f manifest-test.yml

perm_for_chrome:
	chmod 755 integration_tests/chromedriver

int_test:
	python3 integration_tests/main.py

int_test_no_docker:
	python3 integration_tests/main.py --ignore-docker

dockerstack:
	docker-compose -f docker/int_tests.docker-compose.yml down --volumes
	docker build -t django_amp -f - . < docker/django_app.Dockerfile
	docker-compose -f docker/int_tests.docker-compose.yml up

dockerstack_stop:
	docker-compose -f docker/int_tests.docker-compose.yml down
	docker-compose -f docker/int_tests.docker-compose.yml down --volumes
