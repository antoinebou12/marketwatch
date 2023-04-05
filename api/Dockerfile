# syntax=docker/dockerfile:1

FROM python:3.12.0a6-slim

WORKDIR /api

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

COPY api/ .

CMD ["unicorn", "marketwatch:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2"]
