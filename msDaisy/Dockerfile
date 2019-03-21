FROM debian:latest

MAINTAINER Steeve Péré "steevepere@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential curl
RUN pip install flask

COPY . .
ENTRYPOINT ["python"]
CMD ["app.py"]

HEALTHCHECK --interval=3m --timeout=3s \
  CMD curl -f http://localhost:5003/hello || exit 1
