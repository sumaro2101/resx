FROM python:3.11.9-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV HOME=/home/app
ENV PYTHONPATH=/app

COPY pyproject.toml .

RUN apt-get update \
    && pip install --upgrade pip \
    && apt-get install -y build-essential \
    && apt-get install -y libpq-dev \
    && apt-get install -y gettext \
    && apt-get install -y git \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY ./compose/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./compose/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/telegram/start /start-telegram
RUN sed -i 's/\r$//g' /start-telegram
RUN chmod +x /start-telegram

RUN mkdir ./staticfiles \
    && mkdir ./mediafiles

WORKDIR /app

EXPOSE 8000

ENTRYPOINT [ "/entrypoint" ]
