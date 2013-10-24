# -*- coding: utf-8 -*-

import os
import sys
import transaction
from datetime import datetime, date

from sqlalchemy import engine_from_config
from sqlalchemy.exc import IntegrityError
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models import (
    DBSession,
    Group,
    C3sStaff,
    C3sMember,
    Base,
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        accountants_group = Group(name=u"staff")
        staffer1 = C3sStaff(
            login=u"rut",
            password=u"berries",
            email=u"noreply@c3s.cc",
        )
        staffer1.groups = [accountants_group]

        member1 = C3sMember(
            firstname=u"Firstnäme",  # includes umlaut
            lastname=u"Lastname",
            email=u"foo@shri.de",
            password=u"berries",
            address1=u"address one",
            address2=u"address two",
            postcode=u"12345 foo",
            city=u"Footown Mäh",
            country=u"Foocountry",
            locale=u"DE",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u"ABCDEFGHIJ",
            num_shares=u'10',
            date_of_submission=datetime.now(),
            invest_member=True,
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
        )
        #DBSession.add(accountants_group)
        #try:
        #    DBSession.add(staffer1)
        #except:
        #    pass
        #try:
            #DBSession.add(member1)
        #except IntegrityError:
        #    DBSession.remove(member1)
            #pass

        import random
        import string

        for i in range(50):
            print i
            member = C3sMember(
                firstname=u"Firstnäme",  # includes umlaut
                lastname=u"Lastname",
                email=u"foo@shri.de",
                password=u"berries",
                address1=u"address one",
                address2=u"address two",
                postcode=u"12345 foo",
                city=u"Footown Mäh",
                country=u"Foocountry",
                locale=u"DE",
                date_of_birth=date.today(),
                email_is_confirmed=False,
                email_confirm_code=''.join(
                    random.choice(
                        string.ascii_uppercase + string.digits
                    ) for x in range(8)),
                num_shares=u'10',
                date_of_submission=datetime.now(),
                invest_member=True,
                member_of_colsoc=True,
                name_of_colsoc=u"GEMA",
            )
            try:
                DBSession.add(member)
            except IntegrityError:
                DBSession.remove(member)


def init():
    #config_uri = 'development.ini'
    #setup_logging(config_uri)
    #settings = get_appsettings(config_uri)
    #engine = engine_from_config('sqlite://')
    engine = engine_from_config({'sqlalchemy.url': 'sqlite://'})
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        accountants_group = Group(name=u"staff")
        staffer1 = C3sStaff(
            login=u"rut",
            password=u"berries",
            email=u"noreply@c3s.cc",
        )
        staffer1.groups = [accountants_group]

        member1 = C3sMember(
            firstname=u"Firstnäme",  # includes umlaut
            lastname=u"Lastname",
            email=u"foo@shri.de",
            password=u"berries",
            address1=u"address one",
            address2=u"address two",
            postcode=u"12345 foo",
            city=u"Footown Mäh",
            country=u"Foocountry",
            locale=u"DE",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u"ABCDEFGHIJ",
            num_shares=u'10',
            date_of_submission=datetime.now(),
            invest_member=True,
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
        )
        try:
            DBSession.add(accountants_group)
        except IntegrityError:
            DBSession.delete(accountants_group)

        DBSession.add(staffer1)
        if C3sMember.get_by_code(member1.email_confirm_code) is None:
            try:
                DBSession.add(member1)
            except IntegrityError:
                pass


def init_50():
    #config_uri = 'development.ini'
    #setup_logging(config_uri)
    #settings = get_appsettings(config_uri)
    #engine = engine_from_config('sqlite://')
    engine = engine_from_config({'sqlalchemy.url': 'sqlite://'})
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    import random
    import string
    with transaction.manager:
        for i in range(50):
            member = C3sMember(
                firstname=u"Firstnäme",  # includes umlaut
                lastname=u"Lastname",
                email=u"foo@shri.de",
                password=u"berries",
                address1=u"address one",
                address2=u"address two",
                postcode=u"12345 foo",
                city=u"Footown Mäh",
                country=u"Foocountry",
                locale=u"DE",
                date_of_birth=date.today(),
                email_is_confirmed=False,
                email_confirm_code=''.join(
                    random.choice(
                        string.ascii_uppercase + string.digits
                    ) for x in range(8)),
                num_shares=u'10',
                date_of_submission=datetime.now(),
                invest_member=True,
                member_of_colsoc=True,
                name_of_colsoc=u"GEMA",
            )
            try:
                DBSession.add(member)
            except IntegrityError:
                pass
