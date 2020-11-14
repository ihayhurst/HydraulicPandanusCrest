# Dockerfile
FROM python:3.9-slim-buster

RUN apt update && apt install -y libaio1 wget
RUN apt install -y unzip
RUN apt install -y gcc python3-dev
RUN pip install --no-cache-dir --upgrade pip

WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-basic-linux.x64-19.8.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-19.8.0.0.0dbru.zip && \
    rm -f instantclient-basic-linux.x64-19.8.0.0.0dbru.zip 
RUN cd /opt/oracle/instantclient_19_8 && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci
RUN echo /opt/oracle/instantclient_19_8 > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig
RUN  pip install --no-cache-dir cx_Oracle

WORKDIR /app
ADD . /app

RUN        pip install --no-cache-dir -r requirements.txt

# server = "python manage.py runserver 0.0.0.0:8000"
#ENTRYPOINT ["pipenv", "run", "server"]
#uwsgi has wggi.py equivalent run.py configured in in app.ini
CMD ["uwsgi", "app.ini"]
