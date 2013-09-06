# -*- coding: utf-8  -*-
import transaction
#import cryptacular.bcrypt
from datetime import (
    date,
    datetime,
)
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
    Date,
    Unicode
)
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    InvalidRequestError
)
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker
)
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
#crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

#def hash_password(password):
#    return unicode(crypt.encode(password))

class C3sMember(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    firstname = Column(Unicode(255))
    lastname = Column(Unicode(255))
    email = Column(Unicode(255))
    address1 = Column(Unicode(255))
    address2 = Column(Unicode(255))
    postcode = Column(Unicode(255))
    city = Column(Unicode(255))
    country = Column(Unicode(255))
    locale = Column(Unicode(255))
    date_of_birth = Column(Date(), nullable=False)
    email_is_confirmed = Column(Boolean, default=False)
    email_confirm_code = Column(Unicode(255), unique=True)
    num_shares = Column(Integer())  # XXX TODO: check for number <= max_shares
#    is_composer = Column(Boolean())
#    is_lyricist = Column(Boolean())
#    is_producer = Column(Boolean())
#    is_remixer = Column(Boolean())
#    is_dj = Column(Boolean())
    date_of_submission = Column(DateTime(), nullable=False)
    invest_member = Column(Boolean, default=False)
    member_of_colsoc = Column(Boolean, default=False)
    name_of_colsoc = Column(Unicode(255))
#    opt_band = Column(Unicode(255))
#    opt_URL = Column(Unicode(255))

    def __init__(self, firstname, lastname, email,
                 address1, address2, postcode, city, country, locale,
                 date_of_birth, email_is_confirmed, email_confirm_code,
                 num_shares,
                 #is_composer, is_lyricist, is_producer, is_remixer, is_dj,
                 date_of_submission,
                 invest_member, member_of_colsoc, name_of_colsoc,
                 #opt_band, opt_URL
                 ):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.address1 = address1
        self.address2 = address2
        self.postcode = postcode
        self.city = city
        self.country = country
        self.locale = locale
        self.date_of_birth = date_of_birth
        self.email_is_confirmed = email_is_confirmed
        self.email_confirm_code = email_confirm_code
        self.num_shares = num_shares
        #self.is_composer = is_composer
        #self.is_lyricist = is_lyricist
        #self.is_producer = is_producer
        #self.is_remixer = is_remixer
        #self.is_dj = is_dj
        self.date_of_submission = datetime.now()
        self.invest_member = invest_member
        self.member_of_colsoc = member_of_colsoc
        self.name_of_colsoc = name_of_colsoc
        #self.opt_band = opt_band
        #self.opt_URL = opt_URL

    @classmethod
    def get_by_code(cls, email_confirm_code):
        """
        find a member by confirmation code

        this is needed when a user returns from reading her email
        and clicking on a link containing the confirmation code.
        as the code is unique, one record is returned.
        """
        dbSession = DBSession  # ()
        return dbSession.query(cls).filter(
            cls.email_confirm_code == email_confirm_code).first()

    @classmethod
    def check_for_existing_confirm_code(cls, email_confirm_code):
        """
        check if a code is already present
        """
        dbSession = DBSession  # ()
        check = dbSession.query(cls).filter(
            cls.email_confirm_code == email_confirm_code).first()
        if check:  # pragma: no cover
            return True
        else:
            return False

def populate():  # pragma: no coverage: not using this atm
    session = DBSession()
    #model = MyModel(name=u'root', value=55)
    member = C3sMember(
        firstname=u"Firstnäme",  # includes umlaut
        lastname=u"Lastname",
        email=u"foo@shri.de",
        address1=u"address one",
        address2=u"address two",
        postcode=u"12345 foo",
        city=u"Footown Mäh",
        country=u"Foocountry",
        locale=u"DE",
        date_of_birth=date.today(),
        email_is_confirmed=False,
        email_confirm_code=u"ABCDEFGHIJ",
        num_shares=10,
#        is_composer=True,
#        is_lyricist=True,
#        is_producer=True,
#        is_remixer=True,
#        is_dj=True,
        date_of_submission=datetime.now(),
        invest_member=True,
        member_of_colsoc=True,
        name_of_colsoc=u"GEMA",
#        opt_band=u"Moin Meldon",
#        opt_URL=u"http://moin.meldon"
    )
    try:
        #session.add(model)
        session.add(member)
    except InvalidRequestError, e:
        print("InvalidRequestError! %s") % e
    except OperationalError, ope:
        print("OperationalError! %s") % ope
        #pass
    session.flush()
    try:
        transaction.commit()
    except:
        pass
    # pass


def initialize_sql(engine):
    # pass
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError, ie:  # pragma: no cover
        print "--- initialize_sql aborted due to IntegrityError: "
        print ie
        transaction.abort()
        # if data is already present in database the transaction is aborted
