#!/bin/env/python
# -*- coding: utf-8 -*-
# http://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html
#                                            #creating-functional-tests
import unittest
import transaction


def _initTestingDB():
    """
    set up a database to run tests against
    """
    from c3smembership.models import DBSession
    from sqlalchemy import create_engine
    #from c3smembership.models import initialize_sql
    #from c3smembership.models import initialize_sql
    try:
        #session = initialize_sql(create_engine('sqlite:///:memory:'))
        session = create_engine('sqlite:///:memory:')
    except:
        session = DBSession
    return session


class AccountantsFunctionalTests(unittest.TestCase):
    """
    these tests are functional tests to check functionality of the whole app
    (i.e. integration tests)
    they also serve to get coverage for 'main'
    """
    def setUp(self):
        my_settings = {
            'sqlalchemy.url': 'sqlite://',  # where the database is
            'available_languages': 'da de en es fr',
            'c3smembership.offset': '30'}
        #my_other_settings = {'sqlalchemy.url': 'sqlite:///test.db',
        #                     'available_languages': 'da de en es fr'}
                        # mock, not even used!?
        #from sqlalchemy import engine_from_config
        #engine = engine_from_config(my_settings)
       # DBSession = _initTestingDB()
        from c3smembership.scripts.initialize_db import init
        init()
        from c3smembership import main
        #try:
        app = main({}, **my_settings)
        #except:
        #    app = main({}, **my_other_settings)
        #    pass
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        # maybe I need to check and remove globals here,
        # so the other tests are not compromised
        #del engine
        from c3smembership.models import DBSession
        DBSession.close()
        DBSession.remove()

    def test_login_and_dashboard(self):
        """
        load the login form, dashboard, member detail
        """
        #
        # login
        #
        res = self.testapp.get('/login', status=200)
        self.failUnless('login' in res.body)
        # try invalid user
        form = res.form
        form['login'] = 'foo'
        form['password'] = 'bar'
        res2 = form.submit('submit')
        self.failUnless(
            'Please note: There were errors' in res2.body)
        # try valid user & invalid password
        form = res2.form
        form['login'] = 'rut'
        form['password'] = 'berry'
        res3 = form.submit('submit', status=200)
        # try valid user, valid password
        form = res2.form
        form['login'] = 'rut'
        form['password'] = 'berries'
        res3 = form.submit('submit', status=302)
        #
        # being logged in ...
        res4 = res3.follow()
        #print(res4.body)
        self.failUnless(
            'Dashboard' in res4.body)
        # now that we are logged in,
        # the login view should redirect us to the dashboard
        res5 = self.testapp.get('/login', status=302)
        # so yes: that was a redirect
        res6 = res5.follow()
        #print(res4.body)
        self.failUnless(
            'Dashboard' in res6.body)
        # choose number of applications shown
        res6a = self.testapp.get(
            '/dashboard/0',
            status=200,
            extra_environ={
                'num_display': '30',
            }
        )
        #print('res6a:')
        #print res6a
        self.failUnless('<h1>Dashboard</h1>' in res6a.body)
        # try an invalid page number
        res6b = self.testapp.get(
            '/dashboard/foo',
            status=200,
        )
        #print('res6b:')
        #print res6b.body
        self.failUnless(
            '<p>Number of data sets: 1</p>' in res6b.body)
        #
        # member details
        #
        # now look at some members details with nonexistant id
        res7 = self.testapp.get('/detail/5', status=302)
        res7a = res7.follow()
        self.failUnless('Dashboard' in res7a.body)

        # now look at some members details
        res7 = self.testapp.get('/detail/1', status=200)
        self.failUnless('Firstnäme' in res7.body)
        self.failUnless(
            "<td>signature received?</td><td>No</td>" in res7.body)
        self.failUnless(
            "<td>payment received?</td><td>No</td>" in res7.body)

        form = res7.form
        form['signature_received'] = True
        form['payment_received'] = True
        res8 = form.submit('submit')
        #print(res8.body)
        self.failUnless(
            "<td>signature received?</td><td>True</td>" in res8.body)
        self.failUnless(
            "<td>payment received?</td><td>True</td>" in res8.body)
        # finally log out
        res9 = self.testapp.get('/logout', status=302)  # redirects to login
        res10 = res9.follow()
        self.failUnless('login' in res10.body)
#    def test_detail_wrong_id(self):


class FunctionalTests(unittest.TestCase):
    """
    these tests are functional tests to check functionality of the whole app
    (i.e. integration tests)
    they also serve to get coverage for 'main'
    """
    def setUp(self):
        my_settings = {'sqlalchemy.url': 'sqlite://',
                       'available_languages': 'da de en es fr',
                       'c3smembership.mailaddr': 'c@c3s.cc'}
        #my_other_settings = {'sqlalchemy.url': 'sqlite:///test.db',
        #                     'available_languages': 'da de en es fr'}
                        # mock, not even used!?
        #from sqlalchemy import engine_from_config
        #engine = engine_from_config(my_settings)
        from c3smembership.scripts.initialize_db import init
        init()

        from c3smembership import main
        #try:
        app = main({}, **my_settings)
        #except:
        #    app = main({}, **my_other_settings)
        #    pass
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        # maybe I need to check and remove globals here,
        # so the other tests are not compromised
        #del engine
        from c3smembership.models import DBSession
        #DBSession.remove()
        DBSession.close()
        #TODO: delete database
        DBSession.remove()
        #import pdb; pdb.set_trace()

    def test_base_template(self):
        """load the front page, check string exists"""
        res = self.testapp.get('/', status=200)
        self.failUnless('Cultural Commons Collecting Society' in res.body)
        self.failUnless(
            'Copyright 2013, C3S SCE' in res.body)

    # def test_faq_template(self):
    #     """load the FAQ page, check string exists"""
    #     res = self.testapp.get('/faq', status=200)
    #     self.failUnless('FAQ' in res.body)
    #     self.failUnless(
    #         'Copyright 2013, OpenMusicContest.org e.V.' in res.body)

    def test_lang_en_LOCALE(self):
        """load the front page, forced to english (default pyramid way),
        check english string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/?_LOCALE_=en', status=200)
        self.failUnless(
            'Application for Membership of ' in res.body)

    def test_lang_en(self):
        """load the front page, set to english (w/ pretty query string),
        check english string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/?en', status=302)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res1 = res.follow()
        self.failUnless(
            'Application for Membership of ' in res1.body)

# so let's test the app's obedience to the language requested by the browser
# i.e. will it respond to http header Accept-Language?

    # def test_accept_language_header_da(self):
    #     """check the http 'Accept-Language' header obedience: danish
    #     load the front page, check danish string exists"""
    #     res = self.testapp.reset()  # delete cookie
    #     res = self.testapp.get('/', status=200,
    #                            headers={
    #             'Accept-Language': 'da'})
    #     #print(res.body) #  if you want to see the pages source
    #     self.failUnless(
    #         '<input type="hidden" name="_LOCALE_" value="da"' in res.body)

    def test_accept_language_header_de_DE(self):
        """check the http 'Accept-Language' header obedience: german
        load the front page, check german string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get(
            '/', status=200,
            headers={
                'Accept-Language': 'de-DE'})
        #print(res.body) #  if you want to see the pages source
        self.failUnless(
            'Mitgliedschaftsantrag für die' in res.body)
        self.failUnless(
            '<input type="hidden" name="_LOCALE_" value="de"' in res.body)

    def test_accept_language_header_en(self):
        """check the http 'Accept-Language' header obedience: english
        load the front page, check english string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get(
            '/', status=200,
            headers={
                'Accept-Language': 'en'})
        #print(res.body) #  if you want to see the pages source
        self.failUnless(
            "I want to become"
            in res.body)

    # def test_accept_language_header_es(self):
    #     """check the http 'Accept-Language' header obedience: spanish
    #     load the front page, check spanish string exists"""
    #     res = self.testapp.reset()  # delete cookie
    #     res = self.testapp.get('/', status=200,
    #                            headers={
    #             'Accept-Language': 'es'})
    #     #print(res.body) #  if you want to see the pages source
    #     self.failUnless(
    #         'Luego de enviar el siguiente formulario,' in res.body)

    # def test_accept_language_header_fr(self):
    #     """check the http 'Accept-Language' header obedience: french
    #     load the front page, check french string exists"""
    #     res = self.testapp.reset()  # delete cookie
    #     res = self.testapp.get('/', status=200,
    #                            headers={
    #             'Accept-Language': 'fr'})
    #     #print(res.body) #  if you want to see the pages source
    #     self.failUnless(
    #         'En envoyant un courriel à data@c3s.cc vous pouvez' in res.body)

    def test_no_cookies(self):
        """load the front page, check default english string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get(
            '/', status=200,
            headers={
                'Accept-Language': 'af, cn'})  # ask for missing languages
        #print res.body
        self.failUnless('Application for Membership' in res.body)

#############################################################################
# check for validation stuff

    def test_form_lang_en_non_validating(self):
        """load the join form, check english string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/?_LOCALE_=en', status=200)
        form = res.form
        #print(form.fields)
        #print(form.fields.values())
        form['firstname'] = 'John'
        #form['address2'] = 'some address part'
        res2 = form.submit('submit')
        self.failUnless(
            'There was a problem with your submission' in res2.body)

    def test_form_lang_de(self):
        """load the join form, check german string exists"""
        res = self.testapp.get('/?de', status=302)
        #print(res)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res2 = res.follow()
        #print(res2)
        # test for german translation of template text (lingua_xml)
        self.failUnless(
            'Mitgliedschaftsantrag für die' in res2.body)
        # test for german translation of form field label (lingua_python)
        self.failUnless('Vorname' in res2.body)

    def test_form_lang_LOCALE_de(self):
        """load the join form in german, check german string exists
        this time forcing german locale the pyramid way
        """
        res = self.testapp.get('/?_LOCALE_=de', status=200)
        # test for german translation of template text (lingua_xml)
        self.failUnless(
            'Mitgliedschaftsantrag für die' in res.body)
        # test for german translation of form field label (lingua_python)
        self.failUnless('Vorname' in res.body)

###########################################################################
# checking the success page that sends out email with verification link

    def test_check_email_en_wo_context(self):
        """load the page in english, be redirected to the form (data is missing)
        check english string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/check_email?en', status=302)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res1 = res.follow()
        #print(res1)
        self.failUnless(
            'Application for Membership of ' in str(
                res1.body),
            'expected string was not found in web UI')

    def test_verify_email_en_w_good_code(self):
        """load the page in english, be redirected to the form (data is missing)
        check english string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/verify/foo@shri.de/ABCDEFGHIJ', status=200)
        self.failUnless(
            'Password' in res.body)
            #'Your Email has been confirmed, Firstnäme Lastname!' in res.body)
        #res2 = self.testapp.get(
        #    '/C3S_SCE_AFM_Firstn_meLastname.pdf', status=200)
        #self.failUnless(len(res2.body) > 70000)

###########################################################################
# checking the disclaimer

    # def test_disclaimer_en(self):
    #     """load the disclaimer in english (via query_string),
    #     check english string exists"""
    #     res = self.testapp.reset()
    #     res = self.testapp.get('/disclaimer?en', status=302)
    #     self.failUnless('The resource was found at' in res.body)
    #     # we are being redirected...
    #     res1 = res.follow()
    #     self.failUnless(
    #         'you may order your data to be deleted at any time' in str(
    #             res1.body),
    #         'expected string was not found in web UI')

    # def test_disclaimer_de(self):
    #     """load the disclaimer in german (via query_string),
    #     check german string exists"""
    #     res = self.testapp.reset()
    #     res = self.testapp.get('/disclaimer?de', status=302)
    #     self.failUnless('The resource was found at' in res.body)
    #     # we are being redirected...
    #     res1 = res.follow()
    #     self.failUnless(
    #         'Datenschutzerkl' in str(
    #             res1.body),
    #         'expected string was not found in web UI')

    # def test_disclaimer_LOCALE_en(self):
    #     """load the disclaimer in english, check english string exists"""
    #     res = self.testapp.reset()
    #     res = self.testapp.get('/disclaimer?_LOCALE_=en', status=200)
    #     self.failUnless(
    #         'you may order your data to be deleted at any time' in str(
    #             res.body),
    #         'expected string was not found in web UI')

    # def test_disclaimer_LOCALE_de(self):
    #     """load the disclaimer in german, check german string exists"""
    #     res = self.testapp.reset()
    #     res = self.testapp.get('/disclaimer?_LOCALE_=de', status=200)
    #     self.failUnless(
    #         'Datenschutzerkl' in str(
    #             res.body),
    #         'expected string was not found in web UI')

    def test_success_wo_data_en(self):
        """load the success page in english (via query_string),
        check for redirection and english string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/success?en', status=302)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res1 = res.follow()
        #print(res1)
        self.failUnless(  # check text on page redirected to
            'Please fill out the form' in str(
                res1.body),
            'expected string was not found in web UI')

    def test_success_pdf_wo_data_en(self):
        """
        try to load a pdf (which must fail because the form was not used)
        check for redirection to the form and test string exists
        """
        res = self.testapp.reset()
        res = self.testapp.get(
            '/C3S_SCE_AFM_ThefirstnameThelastname.pdf',
            status=302)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res1 = res.follow()
        #print(res1)
        self.failUnless(  # check text on page redirected to
            'Please fill out the form' in str(
                res1.body),
            'expected string was not found in web UI')

    # def test_success_w_data(self):
    #     """
    #     load the form, fill the form, (in one go via POST request)
    #     check for redirection, push button to send verification mail,
    #     check for 'mail was sent' message
    #     """
    #     res = self.testapp.reset()
    #     res = self.testapp.get('/', status=200)
    #     form = res.form
    #     print '*'*80
    #     print '*'*80
    #     print '*'*80
    #     print form.fields
    #     res = self.testapp.post(
    #         '/',  # where the form is served
    #         {
    #             'submit': True,
    #             'firstname': 'TheFirstName',
    #             'lastname': 'TheLastName',
    #             'date_of_birth': '1987-06-05',
    #             'address1': 'addr one',
    #             'address2': 'addr two',
    #             'postcode': '98765 xyz',
    #             'city': 'Devilstown',
    #             'country': 'AF',
    #             'email': 'email@example.com',
    #             'password': 'berries',
    #             'num_shares': '42',
    #             '_LOCALE_': 'en',
    #             #'activity': set(
    #             #    [
    #             #        u'composer',
    #             #        #u'dj'
    #             #    ]
    #             #),
    #             'invest_member': 'yes',
    #             'member_of_colsoc': 'yes',
    #             'name_of_colsoc': 'schmoo',
    #             #'opt_band': 'yes band',
    #             #'opt_URL': 'http://yes.url',
    #             #'noticed_dataProtection': 'yes'
    #             'num_shares': '23',
    #         },
    #         #status=302,  # expect redirection to success page
    #         status=200,  # expect redirection to success page
    #     )

    #     print(res.body)
    #     self.failUnless('The resource was found at' in res.body)
    #     # we are being redirected...
    #     res2 = res.follow()
    #     self.failUnless('Success' in res2.body)
    #     #print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
    #     #print res2.body
    #     #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    #     self.failUnless('TheFirstName' in res2.body)
    #     self.failUnless('TheLastName' in res2.body)
    #     self.failUnless('1987-06-05' in res2.body)
    #     self.failUnless('addr one' in res2.body)
    #     self.failUnless('addr two' in res2.body)
    #     self.failUnless('Devilstown' in res2.body)
    #     self.failUnless('email@example.com' in res2.body)
    #     self.failUnless('schmoo' in res2.body)

    #     # now check for the "mail was sent" confirmation
    #     res3 = self.testapp.post(
    #         '/check_email',
    #         {
    #             'submit': True,
    #             'value': "send mail"
    #         }
    #     )
    #     #print(res3)
    #     self.failUnless(
    #         'An email was sent, TheFirstName TheLastName!' in res3.body)

    # def test_success_and_reedit(self):
    #     """
    #     submit form, check success, re-edit: are the values pre-filled?
    #     """
    #     res = self.testapp.reset()
    #     #res = self.testapp.get('/', status=200)
    #     res = self.testapp.post(
    #         '/',  # where the form is served
    #         {
    #             'submit': True,
    #             'firstname': 'TheFirstNäme',
    #             'lastname': 'TheLastNäme',
    #             'date_of_birth': '1987-06-05',
    #             'address1': 'addr one',
    #             'address2': 'addr two',
    #             'postcode': '98765 xyz',
    #             'city': 'Devilstöwn',
    #             'email': 'email@example.com',
    #             'num_shares': '23',
    #             '_LOCALE_': 'en',
    #             #'activity': set(
    #             #    [
    #             #        'composer',
    #             #        #u'dj'
    #             #    ]
    #             #),
    #             'country': 'AF',
    #             'invest_member': 'yes',
    #             'member_of_colsoc': 'yes',
    #             'name_of_colsoc': 'schmoö',
    #             #'opt_band': 'yes bänd',
    #             #'opt_URL': 'http://yes.url',
    #             #'noticed_dataProtection': 'yes'

    #         },
    #         status=302,  # expect redirection to success page
    #     )

    #     #print(res.body)
    #     self.failUnless('The resource was found at' in res.body)
    #     # we are being redirected...
    #     res2 = res.follow()
    #     self.failUnless('Success' in res2.body)
    #     #print("success page: \n%s") % res2.body
    #     #self.failUnless(u'TheFirstNäme' in (res2.body))

    #     # go back to the form and check the pre-filled values
    #     res3 = self.testapp.get('/')
    #     #print(res3.body)
    #     #print("edit form: \n%s") % res3.body
    #     self.failUnless('TheFirstNäme' in res3.body)
    #     form = res3.form
    #     self.failUnless(form['firstname'].value == u'TheFirstNäme')

    def test_email_confirmation(self):
        """
        test email confirmation
        """
        res = self.testapp.reset()
        res = self.testapp.get('/verify/foo@shri.de/ABCDEFGHIJ', status=200)
        # print(res.body)
        form = res.form
        form['password'] = 'berries'
        res2 =  form.submit('submit')
        #print res2.body
        self.failUnless("Load your PDF..." in res2.body)
        res3 = self.testapp.get(
            '/C3S_SCE_AFM_ThefirstnameThelastname.pdf',
            status=200
        )
        #print("length of result: %s") % len(res2.body)
        self.failUnless(80000 < len(res3.body) < 100000)  # check pdf size

    def test_email_confirmation_wrong_mail(self):
        """
        test email confirmation with a wrong email
        """
        res = self.testapp.reset()
        res = self.testapp.get(
            '/verify/NOTEXISTS@shri.de/ABCDEFGHIJ', status=200)
        #print(res.body)
        self.failUnless("Please enter your password." in res.body)

    def test_email_confirmation_wrong_code(self):
        """
        test email confirmation with a wrong code
        """
        res = self.testapp.reset()
        res = self.testapp.get('/verify/foo@shri.de/WRONGCODE', status=200)
        #print(res.body)
        self.failUnless("Please enter your password." in res.body)

    def test_success_check_email(self):
        """
        test "check email" success page with wrong data:
        this should redirect to the form.
        """
        res = self.testapp.reset()
        res = self.testapp.get('/check_email', status=302)

        res2 = res.follow()
        self.failUnless("Please fill out the form" in res2.body)
