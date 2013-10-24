# -*- coding: utf-8  -*-
import unittest
from pyramid import testing

from c3smembership.models import DBSession


def _initTestingDB():
    """
    set up a database to run tests against
    """
    from sqlalchemy import create_engine
    #from c3smembership.models import initialize_sql
    #from c3smembership.models import initialize_sql
    try:
        #session = initialize_sql(create_engine('sqlite:///:memory:'))
        session = create_engine('sqlite:///:memory:')
    except:
        session = DBSession
    return session


class TestUtilities(unittest.TestCase):
    """
    tests for c3smembership/utils.py
    """
    def setUp(self):
        """
        set up everything for a test case
        """
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
        except:
            pass
        self.session = _initTestingDB()

    def tearDown(self):
        """
        clean up after a test case
        """
        DBSession.remove()
        testing.tearDown()

    def test_generate_pdf_en(self):
        """
        Test pdf generation
        and resulting pdf size
        """
        from c3smembership.views import generate_pdf

        mock_appstruct = {
            'firstname': u'Anne',
            'lastname': u'Gilles',
            'email': u'devnull@c3s.cc',
            'date_of_birth': '1987-06-05',
            'address1': 'addr one',
            'address2': 'addr two',
            'postcode': u'54321',
            'city': u'Müsterstädt',
            'country': u'some country',
            #'opt_band': u'Moin Meldön',
            #'opt_URL': 'http://moin.meldon.foo',
            #'activity': set([u'composer', u'lyricist', u'dj']),
            'member_of_colsoc': 'member_of_colsoc',
            'name_of_colsoc': 'Foo Colsoc',
            'invest_member': 'yes',
            'num_shares': '42',
            #'noticed_dataProtection': 'noticed_dataProtection',
            '_LOCALE_': 'en',
            'date_of_submission': '2013-09-09 08:44:47.251588',
        }

        # a skipTest iff pdftk is not installed
        import subprocess
        from subprocess import CalledProcessError
        try:
            res = subprocess.check_call(
                ["which", "pdftk"], stdout=None)
            if res == 0:
                # go ahead with the tests
                result = generate_pdf(mock_appstruct)

                self.assertEquals(result.content_type,
                                  'application/pdf')
                #print("size of pdf: " + str(len(result.body)))
                # check pdf size
                self.assertTrue(100000 > len(result.body) > 50000)

                # TODO: check pdf for contents

        except CalledProcessError, cpe:  # pragma: no cover
            print("pdftk not installed. skipping test!")
            print(cpe)

    def test_generate_pdf_de(self):
        """
        Test pdf generation
        and resulting pdf size
        """
        from c3smembership.views import generate_pdf

        mock_appstruct = {
            'firstname': u'Anne',
            'lastname': u'Gilles',
            'address1': u'addr one',
            'address2': u'addr two',
            'postcode': u'54321',
            'city': u'Müsterstädt',
            'email': u'devnull@c3s.cc',
            'date_of_birth': u'1987-06-05',
            'country': u'my country',
            #'activity': set([u'composer', u'lyricist', u'dj']),
            #'opt_band': u'Moin Meldön',
            #'opt_URL': 'http://moin.meldon.foo',
            #'member_of_colsoc': 'member_of_colsoc',
            #'name_of_colsoc': 'Foo colsoc',
            'invest_member': u'yes',
            #'noticed_dataProtection': 'noticed_dataProtection',
            'num_shares': u'23',
            '_LOCALE_': 'de',
            'date_of_submission': '2013-09-09 08:44:47.251588',
        }

        # a skipTest iff pdftk is not installed
        import subprocess
        from subprocess import CalledProcessError
        try:
            res = subprocess.check_call(
                ["which", "pdftk"], stdout=None)
            if res == 0:
                # go ahead with the tests
                result = generate_pdf(mock_appstruct)

                self.assertEquals(result.content_type,
                                  'application/pdf')
                #print("size of pdf: " + str(len(result.body)))
                #print(result)
                # check pdf size
                self.assertTrue(100000 > len(result.body) > 50000)

                # TODO: check pdf for contents

        except CalledProcessError, cpe:  # pragma: no cover
            print("pdftk not installed. skipping test!")
            print(cpe)

    def test_generate_csv(self):
        """
        test creation of csv snippet
        """
        from c3smembership.utils import generate_csv
        my_appstruct = {
            #'activity': ['composer', 'dj'],
            'firstname': 'Jöhn',
            'lastname': 'Doe',
            'address1': 'In the Middle',
            'address2': 'Of Nowhere',
            'postcode': '12345',
            'city': 'My Town',
            'email': 'devnull@c3s.cc',
            #'region': 'Hessen',
            'country': 'de',
            'date_of_birth': '1987-06-05',
            'member_of_colsoc': 'yes',
            'name_of_colsoc': 'GEMA FöTT',
            #'opt_URL': u'http://foo.bar.baz',
            #'opt_band': u'Moin Meldn',
            #'consider_joining': u'yes',
            #'noticed_dataProtection': u'yes',
            'invest_member': 'yes',
            'num_shares': "25"
        }
        result = generate_csv(my_appstruct)
        #print("test_generate_csv: the result: %s") % result
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        expected_result = today + ',pending...,Jöhn,Doe,devnull@c3s.cc,In the Middle,Of Nowhere,12345,My Town,de,j,1987-06-05,j,GEMA FöTT,25\r\n'
        # note the \r\n at the end: that is line-ending foo!

        #print("type of today: %s ") % type(today)
        #print("type of result: %s ") % type(result)
        #print("type of expected_result: %s ") % type(expected_result)
        #print("result: \n%s ") % (result)
        #print("expected_result: \n%s ") % (expected_result)
        self.assertEqual(str(result), str(expected_result))

#            result == str(today + ';unknown;pending...;John;Doe;' +
#                          'devnull@c3s.cc;In the Middle;Of Nowhere;' +
#                          '12345;My Town;Hessen;de;j;n;n;n;n;j;j;j;j;j;j'))

    def test_mail_body(self):
        """
        test if mail body is constructed correctly
        and if umlauts work
        """
        #print("test_utils.py:TestUtilities.test_mail_body:\n")
        from c3smembership.utils import make_mail_body
        import datetime
        dob = datetime.date(1999, 1, 1)
        my_appstruct = {
            'activity': [u'composer', u'dj'],
            'firstname': u'Jöhn test_mail_body',
            'lastname': u'Döe',
            'date_of_birth': dob,
            'address1': u'addr one',
            'address2': u'addr two',
            'postcode': u'12345 xyz',
            'city': u'Town',
            'email': u'devnull@c3s.cc',
            'country': u'af',
            'member_of_colsoc': u'yes',
            'name_of_colsoc': u'Buma',
            'invest_member': u'yes',
            'num_shares': u"23",
            #'opt_band': u'the yes',
            #'opt_URL': u'http://the.yes',
            #'noticed_dataProtection': u'yes'
        }
        result = make_mail_body(my_appstruct)

        self.failUnless(u'Jöhn test_mail_body' in result)
        self.failUnless(u'Döe' in result)
        self.failUnless(u'postcode:                       12345 xyz' in result)
        self.failUnless(u'Town' in result)
        self.failUnless(u'devnull@c3s.cc' in result)
        self.failUnless(u'af' in result)
        self.failUnless(u'number of shares                23' in result)
        self.failUnless(
            u'member of coll. soc.:           yes' in result)
        self.failUnless(u"that's it.. bye!" in result)

    # def test_accountant_mail(self):
    #     """
    #     test creation of email Message object
    #     """
    #     from c3sintent.utils import accountant_mail
    #     import datetime
    #     my_appstruct = {
    #         'activity': [u'composer', u'dj'],
    #         'firstname': u'Jöhn test_accountant_mail',
    #         'lastname': u'Doe',
    #         'date_of_birth': datetime.date(1987, 6, 5),
    #         'city': u'Town',
    #         'email': u'devnull@example.com',
    #         'country': u'af',
    #         'member_of_colsoc': u'yes',
    #         'name_of_colsoc': u'Foo Colsoc',
    #         'invest_member': u'yes',
    #         'opt_URL': u'http://the.yes',
    #         'opt_band': u'the yes',
    #         'noticed_dataProtection': u'yes'
    #     }
    #     result = accountant_mail(my_appstruct)

    #     from pyramid_mailer.message import Message

    #     self.assertTrue(isinstance(result, Message))
    #     self.assertTrue('yes@c3s.cc' in result.recipients)
    #     self.failUnless('-----BEGIN PGP MESSAGE-----' in result.body,
    #                     'something missing in the mail body!')
    #     self.failUnless('-----END PGP MESSAGE-----' in result.body,
    #                     'something missing in the mail body!')
    #     self.failUnless(
    #         '[C3S] Yes! a new letter of intent' in result.subject,
    #         'something missing in the mail body!')
    #     self.failUnless('noreply@c3s.cc' == result.sender,
    #                     'something missing in the mail body!')
