FROM debian:latest

MAINTAINER Steeve Péré "steevepere@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential curl
RUN pip3 install flask
RUN pip3 install paramiko

COPY . .
ENTRYPOINT ["python3"]
CMD ["app.py"]

HEALTHCHECK --interval=3m --timeout=3s \
  CMD curl -f http://localhost:5002/containers || exit 1
