# Flask-Auth

[![Build Status](https://travis-ci.com/iamjohnnym/flask-auth.svg?branch=master)](https://travis-ci.com/iamjohnnym/flask-auth)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a4a65c2fa1934ee29e454e2fba330c4c)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=iamjohnnym/flask-auth&amp;utm_campaign=Badge_Grade)
[![Docker Quay](https://quay.io/repository/iamjohnnym/flask-auth/status "Docker Quay")](https://quay.io/repository/iamjohnnym/flask-auth)

A restful service for managing users via jwt authentication.

## Table of contents

- [Flask-Auth](#flask-auth)
  - [Table of contents](#table-of-contents)
  - [Libraries](#libraries)
    - [Python Packages](#python-packages)
    - [Optional Integrations](#optional-integrations)
  - [Usage](#usage)
    - [Docker Compose](#docker-compose)
      - [Build DC](#build-dc)
      - [Test DC](#test-dc)
    - [From Source](#from-source)
      - [Build Source](#build-source)
      - [Test Source](#test-source)
  - [Installation](#installation)
  - [Updating](#updating)
  - [Uninstallation](#uninstallation)
  - [Contributing](#contributing)
  - [License](#license)

## Libraries

[(Back to top)](#table-of-contents)

### Python Packages

- [Poetry](https://poetry.eustace.io/): Python packaging and dependency management
- [Flask](https://palletsprojects.com/p/flask/): Python micro web framework
- [Flask-Restplus](https://flask-restplus.readthedocs.io/en/stable/): Flask-RESTPlus encourages best practices with minimal setup.
- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/): Handles SQLAlchemy database migrations for Flask applications using Alembic.
- [Flask-SqlAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/): Flask-SQLAlchemy, a wrapper to the sqlalchemy orm
- [Flask-Cors](https://flask-cors.readthedocs.io/en/latest/): A Flask extension for handling Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible.
- [Flask-Testing](https://pythonhosted.org/Flask-Testing/): Because test driven is cool
- [Flask-Praetorian](https://github.com/dusktreader/flask-praetorian): Strong, Simple, and Precise security for Flask APIs (using jwt)
- [PostgreSQL](https://www.postgresql.org/): The database of choice

### Optional Integrations

- [Sentry.io](https://sentry.io) :: Sentry is an open-source application monitoring platform that helps you identify issues in real-time.

## Usage

[(Back to top)](#table-of-contents)

### Docker Compose

#### Build DC

```bash
make docker-compose-build
# or
docker-compose up -d --build
```

#### Test DC

```bash
make docker-test
# or
docker-compose run users python manage.py cov
```

### From Source

#### Build Source

```bash
make run
# or
poetry run python manage.py run
```

#### Test Source

```bash
make test
# or
poetry run python manage.py cov
```

## Installation

[(Back to top)](#table-of-contents)

[Poetry](https://poetry.eustace.io/) must be installed.

```bash
git clone https://github.com/iamjohnnym/flask-auth
cd flask-auth
# Make sure it can test successfully
make test
# Get list of valid routes
make routes
# Run app on 127.0.0.1:5000
make run
```

## Updating

[(Back to top)](#table-of-contents)

```bash
git pull
make run # Source
# or
make docker-compose-build # Docker
```

## Uninstallation

[(Back to top)](#table-of-contents)

```bash
make down # shut down all docker-compose related services
cd ../ # move down one directory
rm -rf flask-auth  # delete service directory
```

## Contributing

[(Back to top)](#table-of-contents)

Your contributions are always welcome! Please have a look at the [contribution guidelines](CONTRIBUTING.md) first.

## License

[(Back to top)](#table-of-contents)

Apache License, Version 2.0 2019 - [Johnny Martin](https://github.com/iamjohnnym/). Please have a look at the [LICENSE.md](LICENSE.md) for more details.
