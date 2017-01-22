FROM python:2.7.12
MAINTAINER Alastair Paragas "alastairparagas@gmail.com"

RUN apt-get update && apt-get install -y swig libpulse-dev

ADD pdfminer_install.sh pdfminer_install.sh
ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN chmod +x pdfminer_install.sh && bash -c "./pdfminer_install.sh"

VOLUME /halcyon
EXPOSE 80
