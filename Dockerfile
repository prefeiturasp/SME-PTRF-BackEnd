FROM python:3.12.9-bookworm
ENV PYTHONUNBUFFERED=1
ADD . /code
WORKDIR /code
RUN apt-get update && \
    apt-get install libpq-dev -y && \
    apt-get install libpango-1.0-0 libpangocairo-1.0-0 libharfbuzz0b -y && \
    apt-get install libpango1.0-dev libharfbuzz-dev pkg-config -y && \
    python -m pip --no-cache install -U pip && \
    python -m pip --no-cache install -r requirements/production.txt

ENV LANG=pt_BR.UTF-8
ENV LC_ALL=pt_BR.UTF-8

EXPOSE 8001
