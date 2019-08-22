excludes = \*~ \*.pyc .cache/\* test_\* __pycache__/\*

e?=dev
SERVICE=flask-auth

export ${SERVICE}
export ${e}

.PHONY: clean
clean:
	find . -type f -name '*.pyc' -delete

.PHONY: bandit
bandit:
# Bandit checks for known security flaws, vulnerabilies, general bad
# habits and returns non-zero if threshold is met.  -ll means were looking
# for a severity of medium and confidence of low.
# ['undefined', 'low', 'medium', 'high']
	poetry run bandit -c bandit.yml -r . --format custom \
	--msg-template \
	"{abspath}:{line}: {test_id}[bandit]: {severity}: {msg}"

.PHONY: flake
flake:
	poetry run flake8 service

.PHONY: docker-lint
docker-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

.PHONY: test
test:
	poetry run python manage.py cov

.PHONY: push-converge
push-converge:
	poetry run python-codacy-coverage -r coverage.xml

.PHONY: run
run:
	poetry run python manage.py run

.PHONY: routes
routes:
	poetry run python manage.py routes

.PHONY: seed-db
seed-db:
	poetry run python manage.py seed_db

.PHONY: recreate-db
recreate-db:
	poetry run python manage.py recreate_db


# Docker Compose Commands

.PHONY: docker-seed-db
docker-seed-db:
	docker-compose run users python manage.py seed_db

.PHONY: docker-recreate-db
docker-recreate-db:
	docker-compose run users python manage.py recreate_db

.PHONY: docker-test
docker-test:
	docker-compose run --rm users python manage.py cov

.PHONY: docker-compose-build
docker-compose-build:
	docker-compose up -d --build

.PHONY: down
down:
	docker-compose down
