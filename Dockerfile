FROM python:3.12-alpine AS builder

ARG CODE_DIR

WORKDIR ${CODE_DIR}
RUN pip install pipenv

COPY Pipfile Pipfile.lock ${CODE_DIR}/

# set environment variables
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIPENV_CACHE_DIR=${CODE_DIR}/pipenv_cache/

RUN pipenv sync

# Runtime container from this line
FROM python:3.12-alpine AS runtime
ARG CODE_DIR
ARG USER=djangouser
ARG UGROUP=djangogroup

WORKDIR ${CODE_DIR}
COPY --from=builder ${CODE_DIR}/.venv/ ./.venv/

# Finalise the image here
# activate venv by adding it first in path
ENV VIRTUAL_ENV=${CODE_DIR}/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV STATICFILES_DIR=${CODE_DIR}/staticfiles
ENV MEDIAFILES_DIR=${CODE_DIR}/mediafiles
ENV LOGS_DIR=${CODE_DIR}/logs

RUN addgroup -S ${UGROUP} && adduser -S ${USER} -G ${UGROUP} \
    && mkdir app staticfiles mediafiles logs \
    && chown -R ${USER}:${UGROUP} staticfiles mediafiles logs
COPY ./backend ./app

USER ${USER}

WORKDIR ${CODE_DIR}/app

# entry point used for DB and other services to boot up
# ENTRYPOINT [ "executable" ]
