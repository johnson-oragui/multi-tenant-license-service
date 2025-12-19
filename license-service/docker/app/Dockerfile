FROM python:3.11-slim

RUN set -xe;

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ALLOW_ASYNC_UNSAFE="true"
ENV DJANGO_SETTINGS_MODULE=config.settings.prod

RUN groupadd -r app \
  && useradd --create-home --no-log-init -u 1000 -r -g app app \
  && mkdir /app \
  && chown app:app /app

WORKDIR /app

RUN mkdir /app/requirements/

COPY ./docker/app/entrypoint.sh /usr/local/bin/
ADD ./requirements/* /app/requirements/
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements/prod.txt

ADD . /app

USER app
ENV PATH="${PATH}:/home/app/.local/bin"

EXPOSE 8000
ENTRYPOINT ["tini", "--", "entrypoint.sh"]
CMD ["tini", "--", "uwsgi", "--ini", "uwsgi.ini"]
