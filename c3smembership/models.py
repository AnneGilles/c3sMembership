# -*- coding: utf-8  -*-
import transaction
#import cryptacular.bcrypt
from datetime import (
    date,
    datetime,
)
import cryptacular.bcrypt

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
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
from sqlalchemy.sql import func
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    synonym
)
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
crypt = cryptacular.bcrypt.BCRYPTPasswordManager()


def hash_password(password):
    return unicode(crypt.encode(password))


class Group(Base):
    """
    groups aka roles for users
    """
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Unicode(30), unique=True, nullable=False)

    def __str__(self):
        return 'group:%s' % self.name

    def __init__(self, name):
        self.name = name

#    @classmethod
#    def get_Users_group(cls, groupname="User"):
#        """Choose the right group for users"""
#        dbsession = DBSession()
#        users_group = dbsession.query(
#            cls).filter(cls.name == groupname).first()
#        print('=== get_Users_group:' + str(users_group))
#        return users_group


# table for relation between staffers and groups
staff_groups = Table(
    'staff_groups', Base.metadata,
    Column(
        'staff_id', Integer, ForeignKey('staff.id'),
        primary_key=True, nullable=False),
    Column(
        'group_id', Integer, ForeignKey('groups.id'),
        primary_key=True, nullable=False)
)


class C3sStaff(Base):
    """
    C3S staff may login and do things
    """
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    login = Column(Unicode(255))
    _password = Column('password', Unicode(60))
    last_password_change = Column(
        DateTime,
        default=func.current_timestamp())
    email = Column(Unicode(255))
    groups = relationship(
        Group,
        secondary=staff_groups,
        backref="staff")

    def _init_(self, login, password, email):  # pragma: no cover
        self.login = login
        self.password = password
        self.last_password_change = datetime.now()
        self.email = email

    #@property
    #def __acl__(self):
    #    return [
    #        (Allow,                           # user may edit herself
    #         self.username, 'editUser'),
    #        #'user:%s' % self.username, 'editUser'),
    #        (Allow,                           # accountant group may edit
    #         'group:accountants', ('view', 'editUser')),
    #        (Allow,                           # admin group may edit
    #         'group:admins', ('view', 'editUser')),
    #    ]

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    @classmethod
    def get_by_login(cls, login):
        #dbSession = DBSession()
        return DBSession.query(cls).filter(cls.login == login).first()

    @classmethod
    def check_password(cls, login, password):
        #dbSession = DBSession()
        staffer = cls.get_by_login(login)
        #if staffer is None:  # ?
        #    return False
        #if not staffer:  # ?
        #    return False
        return crypt.check(staffer.password, password)

    # this one is used by RequestWithUserAttribute
    @classmethod
    def check_user_or_None(cls, login):
        """
        check whether a user by that username exists in the database.
        if yes, return that object, else None.
        returns None if username doesn't exist
        """
        login = cls.get_by_login(login)  # is None if user not exists
        return login


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
    signature_received = Column(Boolean, default=False)
    payment_received = Column(Boolean, default=False)
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
        self.signature_received = False
        self.payment_received = False
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

    @classmethod
    def get_by_id(cls, _id):
        """return one member by id"""
        return DBSession.query(cls).filter(cls.id == _id).first()

    @classmethod
    def get_number(cls):
        """return number of members (by counting rows in table)"""
        return DBSession.query(cls).count()

    @classmethod
    def member_listing(cls, order_by, how_many=10):
        q = DBSession.query(cls).all()
        # return q.order_by(order_by)[:how_many]
        return q


def populate():  # pragma: no coverage: not using this atm
    session = DBSession()
    #model = MyModel(name=u'root', value=55)

    # a group for people who do accounting
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
        #import pdb; pdb.set_trace()
        session.add(accountants_group)
    except:
        print("es hat geknallt!!!!!!!!!!!!!!!!!!!!!!!!!! accountants_group")
        #pass
        #transaction.rollback()
        #session.rollback()
    try:
        #session.add(model)
        session.add(staffer1)
    except:
        print("es hat geknallt!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! staffer1")
        #transaction.rollback()
        #session.rollback()
    try:
        session.add(member1)
    except InvalidRequestError:  # this can happen, if a dataset already exists
        pass
        #, e:
        #print("InvalidRequestError! %s") % e
    except:
        print("es hat geknallt!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! member1")
        #transaction.rollback()
        #session.rollback()
#    except OperationalError, ope:
#        print("OperationalError! %s") % ope
        #pass
    session.flush()
    #try:
#        transaction.commit()
    #except:
    #    pass


def initialize_sql(engine):

    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError, ie:  # pragma: no cover
        #print "--- initialize_sql aborted due to IntegrityError: "
        #print ie
        transaction.abort()
        # if data is already present in database the transaction is aborted
