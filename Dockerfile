FROM python:3.9-alpine
ENV TZ=Europe/Berlin
MAINTAINER cnguyen
WORKDIR /project

COPY . .
RUN pip install -r requirements.txt
ADD cronjob cronjob
RUN touch /var/log/cron.log
RUN crontab cronjob
CMD crond && tail -f /var/log/cron.log
