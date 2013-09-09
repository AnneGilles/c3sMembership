# -*- coding: utf-8 -*-

import unittest
#from pyramid.config import Configurator
from pyramid import testing

from c3smembership.models import DBSession


def _initTestingDB():
    from sqlalchemy import create_engine
    from c3smembership.models import initialize_sql
    session = initialize_sql(create_engine('sqlite://'))
    return session


class TestViews(unittest.TestCase):
    """
    very basic tests for the main views
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        DBSession.remove()
        self.session = _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

#     def test_join_membership_view_nosubmit(self):
#         from c3sintent.views import join_membership
#         request = testing.DummyRequest(
#             params={
#                 '_LOCALE_': 'en',  # this stopped working with the newly
#                 }  # #              # introduced #  zpt_renderer :-/
#             )
#         print(str(dir(request)))
#         print("request.params: " + str(request.params.get('_LOCALE_')))
#         result = join_membership(request)
#         self.assertTrue('form' in result)

#     def test_join_membership_non_validating(self):
#         from c3sintent.views import join_membership
#         request = testing.DummyRequest(
#             post={
#                 'submit': True,
#                 '_LOCALE_': 'de'
#                 # lots of values missing
#                 },
#             )
#         result = join_membership(request)

#         self.assertTrue('form' in result)
#         self.assertTrue('There was a problem with your submission'
#                         in str(result))

#     def test_intent_validating(self):
#         """
#         check that valid input to the form produces a pdf
#         - with right content type of response
#         - with a certain size
#         - with appropriate content (form details)
#         and a mail would be sent
#         """
#         from c3sintent.views import declare_intent
#         from pyramid_mailer import get_mailer
#         request = testing.DummyRequest(
#             post={
#                 'submit': True,
#                 'firstname': 'TheFirstName',
#                 'lastname': 'TheLastName',
#                 'date_of_birth': '1987-06-05',
#                 'city': 'Devilstown',
#                 'email': 'email@example.com',
#                 '_LOCALE_': 'en',
#                 'activity': set([u'composer', u'dj']),
#                 'country': 'AF',
#                 'invest_member': 'yes',
#                 'member_of_colsoc': 'yes',
#                 'name_of_colsoc': 'schmoo',
#                 'opt_band': 'yes band',
#                 'opt_URL': 'http://yes.url',
#                 'noticed_dataProtection': 'yes'
#             }
#         )
# #        print(dir(request.params))
#         mailer = get_mailer(request)
#         # skip test iff pdftk is not installed
#         import subprocess
#         from subprocess import CalledProcessError
#         try:
#             res = subprocess.check_call(["which", "pdftk"])
#             if res == 0:

#                 # go ahead with the tests:
#                 # feed the test data to the form/view function
#                 result = declare_intent(request)
                
#                 # at this point -if the test fails- we cannot be sure, whether
#                 # we actually got the PDF or the form we tried to submit
#                 # failed validation, e.g. because the requirements weren't
#                 # fulfilled. let's see...

#                 self.assertEquals(result.content_type,
#                                   'application/pdf')
#                 #print("size of pdf: " + str(len(result.body)))
#                 # check pdf size
#                 self.assertTrue(100000 > len(result.body) > 78000)

#                 # check pdf contents
#                 content = ""
#                 from StringIO import StringIO
#                 resultstring = StringIO(result.body)

#                 import slate
#                 content = slate.PDF(resultstring)

#                 # uncomment to see the text in the PDF produced
#                 print(content)

#                 # test if text shows up as expected
# #                self.assertTrue('TheFirstName' in str(content))
# #                self.assertTrue('TheLastName' in str(content))
# #                self.assertTrue('Address1' in str(content))
# #                self.assertTrue('Address2' in str(content))
# #                self.assertTrue('email@example.com' in str(content))
# #                self.assertTrue('Afgahnistan' in str(content))

#                 # check outgoing mails
#                 self.assertTrue(len(mailer.outbox) == 1)
#                 self.assertTrue(
#                     mailer.outbox[
#                         0].subject == "[c3s] Yes! a new letter of intent")

#         except CalledProcessError, cpe:  # pragma: no cover
#             print("pdftk not installed. skipping test!")
#             print(cpe)
