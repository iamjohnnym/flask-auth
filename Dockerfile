# base image
FROM python:3.7.0-alpine

# set working directory
WORKDIR /usr/src/app

SHELL ["/bin/ash", "-eo", "pipefail", "-c"]
# install poetry
# hadolint ignore=DL3018,SC1090
RUN apk --no-cache add --virtual build-deps curl \
    && curl -sSL "https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py" | python \
    # shellcheck source=/root/.poetry/env
    && . "${HOME}/.poetry/env" \
    && poetry config settings.virtualenvs.create false

COPY ./pyproject.toml /usr/src/app/pyproject.toml
# I dont know if you should exist, yet.
# ADD ./poetry.lock /usr/src/app/poetry.lock

# hadolint ignore=DL3018,SC1090
RUN apk --no-cache add postgresql-dev

# hadolint ignore=DL3018,SC1090
RUN apk --no-cache add --virtual build-deps git gcc python-dev musl-dev libffi-dev libc-dev \
    # shellcheck source=/root/.poetry/env
    && . "${HOME}/.poetry/env" \
    && poetry install

# add app
COPY ./ /usr/src/app

# run server
CMD ["/usr/src/app/entrypoint.sh"]
