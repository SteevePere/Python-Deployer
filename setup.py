#!/usr/bin/env python3
"""Installs module"""

from setuptools import setup


with open('requirements.txt') as file:
    requirements = file.read().splitlines()  # getting pip packages from requirements file

setup(
   name='my_deployer',
   version='1.0',
   description='Deploy your applications to a remote Docker automatically',
   author='Steeve Péré',
   author_email='pere_s@etna-alternance.net',
   url="https://github.com/SteevePere/my_deployer",
   packages=['my_deployer'],
   install_requires=requirements
)
