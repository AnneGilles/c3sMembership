#!/usr/bin/env sh
#
# continuous integration shell script to set up the project and run tests
#
#
# apt-get install python-virtualenv
# create a virtualenv, preferrably with the python 2.7 variant:
virtualenv env
# update setuptools if neccessary
env/bin/pip install --upgrade setuptools
# set it up
# this will take a little while and install all necessary dependencies.
env/bin/python setup.py develop
# run the tests
env/bin/nosetests c3smembership/
# this is how you can run individial tests:
#env/bin/nosetests c3smembership/tests/test_webtest.py:FunctionalTests.test_faq_template
