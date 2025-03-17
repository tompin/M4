FROM python:3.11.11-slim-bullseye
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./apps/requirements.txt /app
RUN apt-get update \
  && apt-get install -y netcat postgresql-client libgl1 libglib2.0-0
RUN pip install -U pip setuptools wheel
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY . /app

RUN chmod +x /app/docker-entrypoint.sh

# run entrypoint.sh which will create/apply migrations
ENTRYPOINT ["bash", "/app/docker-entrypoint.sh"]