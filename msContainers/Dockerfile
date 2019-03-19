FROM debian:latest

MAINTAINER Steeve Péré "steevepere@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install flask

COPY . .
ENTRYPOINT ["python"]
CMD ["app.py"]
