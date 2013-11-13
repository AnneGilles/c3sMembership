# -*- coding: utf-8 -*-

import unittest
#from pyramid.config import Configurator
from pyramid import testing

from c3smembership.models import DBSession


def _initTestingDB():
    #from sqlalchemy import create_engine
    #from c3smembership.models import initialize_sql
    #session = initialize_sql(create_engine('sqlite://'))
    session = DBSession
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

    def test_show_success(self):
        """
        test the success page
        """
        from c3smembership.views import show_success
        self.config.add_route('join', '/')
        request = testing.DummyRequest(
            params={
                'appstruct': {
                    'firstname': 'foo',
                    'lastname': 'bar',
                }
            }
        )
        request.session['appstruct'] = {
            'person': {
                'firstname': 'foo',
                'lastname': 'bar',
            }
        }
        result = show_success(request)
        #print result
        self.assertTrue(result['lastname'] is 'bar')
        self.assertTrue(result['firstname'] is 'foo')

    def test_success_check_email(self):
        """
        test the success_check_email view
        """
        from c3smembership.views import success_check_email
        self.config.add_route('join', '/')
        from pyramid_mailer import get_mailer
        request = testing.DummyRequest(
            params={
                'appstruct': {
                    'firstname': 'foo',
                    'lastname': 'bar',
                }
            }
        )
        request.session['appstruct'] = {
            'person': {
                'firstname': 'foo',
                'lastname': 'bar',
                'email': 'bar@shri.de',
            },
            'email_confirm_code': '12345678',
        }
        mailer = get_mailer(request)
        result = success_check_email(request)
        print result
        self.assertTrue(result['lastname'] is 'bar')
        self.assertTrue(result['firstname'] is 'foo')

        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(
            mailer.outbox[0].subject,
            'C3S: confirm your email address and load your PDF')
        #self.assertEqual(mailer.outbox[0]., "hello world")

        verif_link = "https://pretest.c3s.cc/verify/bar@shri.de/12345678"
        self.assertTrue("hello foo bar !" in mailer.outbox[0].body)
        self.assertTrue(verif_link in mailer.outbox[0].body)

    def test_success_check_email_redirect(self):
        """
        test the success_check_email view redirection when appstruct is missing
        """
        from c3smembership.views import success_check_email
        self.config.add_route('join', '/')
        from pyramid_mailer import get_mailer
        request = testing.DummyRequest()
        result = success_check_email(request)

        self.assertEqual('302 Found', result._status)
        self.assertEqual('http://example.com/', result.location)
        #import pdb
        #pdb.set_trace()

    def test_success_verify_email(self):
        """
        test the success_verify_email view
        """
        from c3smembership.views import success_verify_email
        self.config.add_route('join', '/')
        from pyramid_mailer import get_mailer
        # without submitting
        request = testing.DummyRequest()
        request.matchdict['email'] = 'foo@shri.de'
        request.matchdict['code'] = '12345678'
        result = success_verify_email(request)
        self.assertEqual(
            request.session.peek_flash('message_above_form'),
            [u'Please enter your password.'])
        self.assertEqual(result['result_msg'], 'something went wrong.')
        self.assertEqual(result['firstname'], '')
        self.assertEqual(result['lastname'], '')
        self.assertEqual(result['post_url'], '/verify/foo@shri.de/12345678')
        self.assertEqual(result['namepart'], '')
        self.assertEqual(result['correct'], False)

        # TODO: try to submit, maybe in webtest?

    # def test_success_verify_email_(self):
    #     """
    #     test the success_verify_email view
    #     """
    #     from c3smembership.views import success_verify_email
    #     self.config.add_route('join', '/')
    #     #from pyramid_mailer import get_mailer
    #     # without submitting
    #     request = testing.DummyRequest()
    #     request.matchdict['email'] = 'MMMMMMMMMMMMMMMMM@shri.de'
    #     request.matchdict['code'] = '12345678'
    #     request.POST['submit'] = True
    #     result = success_verify_email(request)
    #     self.assertEqual(
    #         request.session.peek_flash('message_above_form'),
    #         [u'Please enter your password.'])
    #     self.assertEqual(result['result_msg'], 'something went wrong.')
    #     self.assertEqual(result['firstname'], '')
    #     self.assertEqual(result['lastname'], '')
    #     self.assertEqual(result['post_url'], '/verify/MMMMMMMMMMMMMMMMM@shri.de/ABCDEFGHIJ')
    #     self.assertEqual(result['namepart'], '')
    #     self.assertEqual(result['correct'], False)

        # TODO: try to submit, maybe in webtest?

#    def _makeLocalizer(self, *arg, **kw):
#        from pyramid.i18n import Localizer
#        return Localizer(*arg, **kw)

#     def test_join_c3s(self):
#         """
#         test the join form
#         """
#         from c3smembership.views import join_c3s
#         request = testing.DummyRequest()
#         from pyramid.i18n import get_localizer
#         from pyramid.threadlocal import get_current_request
#         from pkg_resources import resource_filename
#         import deform

#         def translator(term):
#             return get_localizer(get_current_request()).translate(term)

#         my_template_dir = resource_filename('c3smembership', 'templates/')
#         deform_template_dir = resource_filename('deform', 'templates/')
#         zpt_renderer = deform.ZPTRendererFactory(
#             [
#                 my_template_dir,
#                 deform_template_dir,
#             ],
#             translator=translator,
#         )
#         request.localizer = self._makeLocalizer('en_US', None)

# #        import pdb
# #        pdb.set_trace()

#         #result = join_c3s(request)

    # def test_dashboard_view(self):
    #     from c3smembership.accountants_views import accountants_desk
    #     request = testing.DummyRequest(
    #         params={
    #             'numdisplay': '20',  # this stopped working with the newly
    #         }
    #     )
    #     print(str(dir(request)))
    #     print("request.params: " + str(request.params.get('_LOCALE_')))
    #     result = accountants_desk(request)
    #     self.assertTrue('form' in result)
        #import pdb
        #pdb.set_trace()

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
