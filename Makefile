init:
	docker-compose up -d \
		&& pip install --upgrade pip \
		&& pip install pipenv \
		&& pipenv install -d \
		&& npm i \
		&& python3 -c 'from pulp import *; pulp()' ./pulp/accessibility_monitoring_platform_settings.json \
		&& python3 -c 'from pulp import *; pulp()' ./pulp/report_viewer_settings.json \
		&& psql postgres://admin:secret@localhost:5432/postgres -c "create database accessibility_monitoring_app;" \
		&& python prepare_local_db.py \
		&& ./manage.py migrate \
		&& echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@email.com', 'admin@email.com', 'secret')" | python manage.py shell \
		&& echo "email: admin@email.com & password: secret"

clean_local:
	docker-compose down
	rm -rf ./data
	rm -rf ./node_modules
	rm -rf ./venv
	rm ./.env

start:
	python manage.py runserver 8081

start_report_viewer:
	python manage_report_viewer.py runserver 8082 

static_files_process_accessibility_monitoring_platform:
	python3 -c 'from pulp import *; pulp()' ./pulp/accessibility_monitoring_platform_settings.json

static_files_process_report_viewer:
	python3 -c 'from pulp import *; pulp()' ./pulp/report_viewer_settings.json

static_files_process:
	make static_files_process_accessibility_monitoring_platform
	make static_files_process_report_viewer

watch_accessibility_monitoring_platform:
	npx nodemon -e scss,js --watch accessibility_monitoring_platform/static/scss --watch accessibility_monitoring_platform/static/js --exec "python3 -c 'from pulp import *; pulp()' ./pulp/accessibility_monitoring_platform_settings.json"

watch_report_viewer:
	npx nodemon -e scss,js --watch report_viewer/static/scss --watch report_viewer/static/js --exec "python3 -c 'from pulp import *; pulp()' ./pulp/report_viewer_settings.json"

sync_accessibility_monitoring_platform:
	npx browser-sync start -p http://127.0.0.1:8081/ \
		--files "./accessibility_monitoring_platform/**/*.py" \
		--files "./accessibility_monitoring_platform/**/*.html" \
		--files "./accessibility_monitoring_platform/static/compiled/*.scss" \
		--files "./accessibility_monitoring_platform/static/compiled/**" \
		--watchEvents change --watchEvents add \
		--reload-delay 500

sync_report_viewer:
	npx browser-sync start -p http://127.0.0.1:8082/ \
		--files "./report_viewer/**/*.py" \
		--files "./report_viewer/**/*.html" \
		--files "./report_viewer/static/compiled/*.scss" \
		--files "./report_viewer/static/compiled/**" \
		--watchEvents change --watchEvents add \
		--reload-delay 500

test_accessibility_monitoring_platform:
	python manage.py collectstatic --noinput \
		&& coverage run -m -p pytest --ignore="stack_tests/"  --ignore="report_viewer/" -c pytest.ini \
		&& coverage run --source='./accessibility_monitoring_platform/' -p manage.py test accessibility_monitoring_platform/ \
		&& coverage combine \
		&& coverage report --skip-covered \
		&& coverage erase

test_report_viewer:
	python manage_report_viewer.py collectstatic --noinput \
		&& coverage run -m -p pytest --ignore="stack_tests/"  --ignore="accessibility_monitoring_platform/" -c pytest_report_viewer.ini \
		&& coverage combine \
		&& coverage report --skip-covered \
		&& coverage erase

test:
	make test_accessibility_monitoring_platform
	make test_report_viewer

local_deploy:
	pipenv lock -r > requirements.txt
	cf push -f manifest-test.yml

int_test:
	pipenv lock -r > requirements.txt
	python3 stack_tests/main.py

deploy_prototype:
	python deploy_feature_to_paas/main.py -b up -s deploy_feature_to_paas/deploy_feature_settings.json

breakdown_prototype:
	python deploy_feature_to_paas/main.py -b down -s deploy_feature_to_paas/deploy_feature_settings.json

staging_env:
	python deploy_feature_to_paas/main.py -b up -s deploy_feature_to_paas/deploy_staging_settings.json -f true
	python3 stack_tests/main.py -s ./stack_tests/smoke_tests_stage_env_settings.json
	python3 stack_tests/main.py -s ./stack_tests/smoke_tests_report_viewer_stage_env_settings.json
	python deploy_feature_to_paas/main.py -b down -s deploy_feature_to_paas/deploy_staging_settings.json

docker_is_running = $(shell curl -s -w "%{http_code}\n" http://0.0.0.0:8001 -o /dev/null)

int_test_developer_mode:
    ifneq ($(docker_is_running), 302)
		echo "Launching integration stack"
		docker compose -f stack_tests/docker-compose.yml up -d
    endif
	python3 stack_tests/main.py -s ./stack_tests/integration_tests_developer_mode_settings.json
