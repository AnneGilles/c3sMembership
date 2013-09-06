#!/usr/bin/env sh

# apt-get install python-virtualenv
virtualenv env

env/bin/pip install --upgrade setuptools

env/bin/python setup.py develop

env/bin/ini...
