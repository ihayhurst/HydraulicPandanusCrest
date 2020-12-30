# Dockerfile
FROM python:3.9-slim-buster

RUN apt update && apt install -y libaio1 wget libpcre3 libpcre3-dev gcc python3-dev
RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app
ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

#uwsgi has wggi.py equivalent run.py configured in in app.ini
ENV MPLCONFIGDIR=/tmp/
CMD ["uwsgi", "app.ini"]
