FROM python:3-alpine

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /app