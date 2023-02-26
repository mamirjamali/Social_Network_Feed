FROM python:3.11-alpine
LABEL maintainer="Amir Jamali"

ENV PYTHONUNBUFFERED 1

COPY ./requirments.txt /tmp/requirments.txt
COPY ./requirments.dev.txt /tmp/requirments.dev.txt
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    #Install psycopg2 dependencies to let it be installed on alpine image
    apk add --update --no-cache postgresql-client jpeg-dev && \ 
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev gcc libpq-dev python3-dev \
    musl-dev linux-headers zlib zlib-dev && \
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
    django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts


ENV PATH="/scripts:/py/bin:$PATH"


USER django-user

CMD [ "run.sh" ]