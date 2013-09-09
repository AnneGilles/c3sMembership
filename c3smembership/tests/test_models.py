# -*- coding: utf-8  -*-
import unittest
from pyramid.config import Configurator
from pyramid import testing

DEBUG = False


def _initTestingDB():
    from sqlalchemy import create_engine
    from c3smembership.models import DBSession
    from c3smembership.models import Base
    from c3smembership.models import initialize_sql
    engine = create_engine('sqlite:///:memory:')
    #session = initialize_sql(create_engine('sqlite:///:memory:'))
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession


class C3sMembershipModelTests(unittest.TestCase):
    def setUp(self):
        try:
            #self.session.remove()
            self.session.close()
            print("C3sMembershipModelTests.setUp: removed DB session")
        except:
            pass
        self.session = _initTestingDB()
#        self.session.remove()
#        print "setUp(): type(self.session): " + str(type(self.session))
#        print "setUp(): dir(self.session): " + str(dir(self.session))

    def tearDown(self):
        #print dir(self.session)
        self.session.remove()
        #pass

    def _getTargetClass(self):
        from c3smembership.models import C3sMember
        return C3sMember

    from datetime import (
        date,
        datetime
    )

    def _makeOne(self,
                 firstname=u'SomeFirstnäme',
                 lastname=u'SomeLastnäme',
                 email=u'some@email.de',
                 address1=u"addr one",
                 address2=u"addr two",
                 postcode="12345",
                 city=u"Footown Mäh",
                 country=u"Foocountry",
                 locale=u"DE",
                 date_of_birth=date.today(),
                 email_is_confirmed=False,
                 email_confirm_code=u'ABCDEFGHIK',
                 #is_composer=True,
                 #is_lyricist=True,
                 #is_producer=True,
                 #is_remixer=True,
                 #is_dj=True,
                 date_of_submission=date.today(),
                 invest_member=True,
                 member_of_colsoc=True,
                 name_of_colsoc=u"GEMA",
                 #opt_band=u"Moin Meldon",
                 #opt_URL=u"http://moin.meldon",
                 num_shares=u'23',
                 ):
        #print "type(self.session): " + str(type(self.session))
        return self._getTargetClass()(
            firstname, lastname, email,
            address1, address2, postcode,
            city, country, locale,
            date_of_birth, email_is_confirmed, email_confirm_code,
            num_shares,
            #is_composer, is_lyricist, is_producer, is_remixer, is_dj,
            date_of_submission,
            invest_member, member_of_colsoc, name_of_colsoc,
            #opt_band, opt_URL
            )

    def test_constructor(self):
        instance = self._makeOne()
        #print(instance.firstname)
        self.assertEqual(instance.firstname, u'SomeFirstnäme', "No match!")
        self.assertEqual(instance.lastname, u'SomeLastnäme', "No match!")
        self.assertEqual(instance.email, u'some@email.de', "No match!")
        self.assertEqual(instance.address1, u'addr one', "No match!")
        self.assertEqual(instance.address2, u'addr two', "No match!")
        self.assertEqual(instance.email, u'some@email.de', "No match!")
        self.assertEqual(
            instance.email_confirm_code, u'ABCDEFGHIK', "No match!")
        self.assertEqual(instance.email_is_confirmed, False, "expected False")

    def test_get_by_code(self):
        instance = self._makeOne()
        #session = DBSession()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_code('ABCDEFGHIK')
        #self.session.commit()
        #self.session.remove()
        #print instance_from_DB.email
        if DEBUG:
            print "myMembershipSigneeClass: " + str(myMembershipSigneeClass)
            #        print "str(myUserClass.get_by_username('SomeUsername')): "
            # + str(myUserClass.get_by_username('SomeUsername'))
            #        foo = myUserClass.get_by_username(instance.username)
            #        print "test_get_by_username: type(foo): " + str(type(foo))
        self.assertEqual(instance.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.email, u'some@email.de')

    # def test_check_for_existing_confirm_code(self):
    #     instance = self._makeOne()
    #     self.session.add(instance)
    #     myMembershipSigneeClass = self._getTargetClass()
    #     instance_from_DB = myMembershipSigneeClass.get_by_code('ABCDEFGHIK')
    #     print instance_from_DB.email
    #     if DEBUG:
    #         print "myMembershipSigneeClass: " + str(myMembershipSigneeClass)
    #         #        print "str(myUserClass.get_by_username('SomeUsername')): "
    #         # + str(myUserClass.get_by_username('SomeUsername'))
    #         #        foo = myUserClass.get_by_username(instance.username)
    #         #        print "test_get_by_username: type(foo): " + str(type(foo))
    #     self.assertEqual(instance.firstname, 'SomeFirstname')
    #     self.assertEqual(instance_from_DB.email, 'some@email.de')
