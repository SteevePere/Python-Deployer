FROM debian:latest

MAINTAINER Steeve Péré "steevepere@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install flask

COPY ./app ./app
RUN ls -a .
WORKDIR /app
ENTRYPOINT ["python"]
CMD ["app.py"]
