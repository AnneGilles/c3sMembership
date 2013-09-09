#!/usr/bin/env sh

# apt-get install python-virtualenv
virtualenv env

env/bin/pip install --upgrade setuptools

env/bin/python setup.py develop

env/bin/nosetests c3smembership/
# this is how you can run individial tests:
#env/bin/nosetests c3smembership/tests/test_webtest.py:FunctionalTests.test_faq_template
