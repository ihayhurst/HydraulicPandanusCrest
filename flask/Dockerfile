# Dockerfile
#FROM python:3.9-slim-buster
#RUN apt update && apt install -y  libpcre3 libpcre3-dev gcc 
FROM registry.access.redhat.com/ubi8/python-39
USER root
RUN dnf update -y && rm -rf /var/cache/yum
RUN dnf install -y pcre pcre-devel gcc redhat-lsb-core
COPY requirements.txt  requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

USER 1001
WORKDIR /app
ADD . /app


#uwsgi has wggi.py equivalent run.py configured in in app.ini
ENV MPLCONFIGDIR=/tmp/
CMD ["uwsgi", "app.ini"]
