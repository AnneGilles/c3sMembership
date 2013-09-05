c3sMembership README
====================
This webapp offers a form to to join *Cultural Commons Collecting Society (C3S)*
as member. A GnuPG encrypted mail with the details submitted will be sent to C3S.

When the form is submitted,
form submission data is used to populate a pdf with form fields (using fdf
and pdftk) and the resulting PDF is ready for download.

Another special feature of this app is internationalisation (i18n), making
the form available in several languages. You can help translate this app on
transifex: https://www.transifex.com/projects/p/... tba .../

Help via screencast is available: http://translate.c3s.cc
Also see ./tx/README.rst for more help on the translation machinery.


setup
-----

create a virtualenv, preferrably with the python 2.7 variant:

$ virtualenv env

activate your new virtualenv:

$ . env/bin/activate

get ready for development:

$ python setup.py develop

this will take a little while and install all necessary dependencies.


run (in development mode)
-------------------------

$ pserve development.ini --reload

The app will rebuild templates and reload code whenever it changes.


run (in production mode, daemon mode)
-------------------------------------

$ pserve production.ini start
