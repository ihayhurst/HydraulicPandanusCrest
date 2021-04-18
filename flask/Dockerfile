# Dockerfile
FROM python:3.9-slim-buster

RUN apt update && apt install -y libaio1 wget libpcre3 libpcre3-dev gcc python3-dev
COPY requirements.txt  requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
ADD . /app


#uwsgi has wggi.py equivalent run.py configured in in app.ini
ENV MPLCONFIGDIR=/tmp/
CMD ["uwsgi", "app.ini"]
