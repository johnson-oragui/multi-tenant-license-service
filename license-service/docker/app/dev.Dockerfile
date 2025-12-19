FROM python:3.11-bullseye

RUN set -xe;

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ALLOW_ASYNC_UNSAFE="true"
ENV DJANGO_SETTINGS_MODULE=config.settings.dev

RUN groupadd -r app \
  && useradd --create-home --no-log-init -u 1000 -r -g app app \
  && mkdir /app \
  && chown app:app /app

WORKDIR /app

RUN mkdir /app/requirements/
ADD ./requirements/* /app/requirements/
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements/dev.txt

ADD . /app

USER app

EXPOSE 8000
CMD python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000
