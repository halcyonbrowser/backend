FROM python:2.7.12
MAINTAINER Alastair Paragas "alastairparagas@gmail.com"

RUN apt-get update && apt-get install -y swig libpulse-dev

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

VOLUME /halcyon
EXPOSE 80
