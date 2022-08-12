FROM python:3
MAINTAINER cnguyen
WORKDIR /project

COPY . .
RUN pip install -r requirements.txt
