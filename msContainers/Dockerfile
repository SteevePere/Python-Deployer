FROM debian:latest

MAINTAINER Steeve Péré "steevepere@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential
RUN pip3 install flask
RUN pip3 install paramiko

COPY . .
ENTRYPOINT ["python3"]
CMD ["app.py"]
