# Dockerfile
FROM python:3.9-slim-buster

RUN apt update && apt install -y libaio1 wget
RUN apt install -y unzip
RUN apt install -y gcc python3-dev
RUN pip install --no-cache-dir --upgrade pip


WORKDIR /app
ADD . /app

RUN        pip install --no-cache-dir -r requirements.txt

# server = "python manage.py runserver 0.0.0.0:8000"
#ENTRYPOINT ["pipenv", "run", "server"]
#uwsgi has wggi.py equivalent run.py configured in in app.ini
CMD ["uwsgi", "app.ini"]
