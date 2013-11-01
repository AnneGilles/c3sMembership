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
# populate the database
env/bin/initialize_c3sMembership_db development.ini
# prepare for tests
env/bin/pip install nose coverage pep8 pylint pyflakes
# run the tests
env/bin/nosetests c3smembership/   --with-coverage --cover-html --with-xunit
# this is how you can run individial tests:
#env/bin/nosetests c3smembership/tests/test_webtest.py:FunctionalTests.test_faq_template

# for pyflakes
find c3smembership -regex '.*.py' ! -regex '.*tests.*'|egrep -v '^./tests/'|xargs env/bin/pyflakes  > pyflakes.log || :
# for pylint
rm -f pylint.log
for f in `find c3smembership -regex '.*.py' ! -regex '.*tests.*'|egrep -v '^./tests/'`; do
env/bin/pylint --output-format=parseable --reports=y $f >> pylint.log
done || :
