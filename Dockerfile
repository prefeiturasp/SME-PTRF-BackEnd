FROM python:3.12.9-bullseye
ENV PYTHONUNBUFFERED=1
ADD . /code
WORKDIR /code

# Adicionar repositório para versões mais novas
RUN echo "deb http://deb.debian.org/debian bookworm main" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install libpq-dev -y && \
    apt-get install -t bookworm libpango-1.0-0=1.56.3* libpangocairo-1.0-0=1.56.3* -y && \
    apt-get install -t bookworm libharfbuzz0b=11.2.0* -y && \
    apt-get install -t bookworm libfontconfig1=2.16.0* -y && \
    apt-get install -t bookworm libpango1.0-dev=1.56.3* libharfbuzz-dev=11.2.0* pkg-config -y && \
    python -m pip --no-cache install -U pip && \
    python -m pip --no-cache install -r requirements/production.txt

ENV LANG=pt_BR.UTF-8
ENV LC_ALL=pt_BR.UTF-8

EXPOSE 8001
