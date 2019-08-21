# base image
FROM python:3.7.0-alpine

# install dependencies
# RUN apk update && \
#    apk add --virtual git build-deps gcc python-dev musl-dev libffi-dev libc-dev ; \
#    apk add postgresql-dev ; \
#    apk add netcat-openbsd

# set working directory
WORKDIR /usr/src/app

# install poetry
RUN pip install poetry ; \
    poetry config settings.virtualenvs.create false

ADD ./pyproject.toml /usr/src/app/pyproject.toml
# I dont know if you should exist, yet.
# ADD ./poetry.lock /usr/src/app/poetry.lock

# RUN poetry run pip install --upgrade pip

# install dependencies
# RUN poetry install
# RUN apk del .build-deps gcc

RUN apk --update add postgresql-dev
RUN apk --update add --virtual build-deps git gcc python-dev musl-dev libffi-dev libc-dev \
  && poetry install \
  && apk del build-deps

# add app
COPY . /usr/src/app

# run server
CMD ["/usr/src/app/entrypoint.sh"]
