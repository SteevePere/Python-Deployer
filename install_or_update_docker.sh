#!/bin/bash

apt-get purge docker-ce -y  # removing Docker

apt-get update -y  # updating apt

apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg2 \
    software-properties-common

curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -  # setting up repository

add-apt-repository \  # adding repository
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

apt-get update -y

apt-get install -y docker-ce=5:18.09.3~3-0~debian-stretch docker-ce-cli=5:18.09.3~3-0~debian-stretch containerd.io  # installing Docker 18.09
