FROM python:3.11-alpine
LABEL maintainer="Amir Jamali"

ENV PYTHONUNBUFFERED 1

COPY ./requirments.txt /tmp/requirments.txt
COPY ./requirments.dev.txt /tmp/requirments.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    #Install psycopg2 dependencies to let it be installed on alpine image
    apk add --update --no-cache postgresql-client && \ 
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev gcc libpq-dev python3-dev \
        musl-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirments.txt && \
    if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirments.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    #Delete the group of dependencies
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

ENV PATH="/py/bin:$PATH"

USER django-user