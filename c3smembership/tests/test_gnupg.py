#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import shutil
from pyramid import testing

from c3smembership.models import DBSession


def _initTestingDB():
    from sqlalchemy import create_engine
    #from c3smembership.models import initialize_sql
    #session = initialize_sql(create_engine('sqlite://'))
    from c3smembership.scripts import initialize_db
    session = initialize_db.init()
# initialize_db.main()

    return session


class TestGnuPG(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        #import pdb; pdb.set_trace()
        #shutil.move('c3sMembership.db', 'c3sMembership.db.old')
        DBSession.remove()
        self.session = _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        #shutil.rm('c3sMembership.db')
        testing.tearDown()

    def test_encrypt_with_gnupg_w_umlauts(self):
        """
        test if unicode input is acceptable and digested
        """
        from c3smembership.gnupg_encrypt import encrypt_with_gnupg
        result = encrypt_with_gnupg(u'fuck the umläuts')
        #print ("the result: " + str(result))
        self.assertTrue('-----BEGIN PGP MESSAGE-----' in str(result))
        self.assertTrue('-----END PGP MESSAGE-----' in str(result))

    def test_encrypt_with_gnupg_import_key(self):
        """
        test if encryption produces any result at all
        """
        from c3smembership.gnupg_encrypt import encrypt_with_gnupg
        result = encrypt_with_gnupg('foo')
        #print ("the result: " + str(result))
        self.assertTrue('-----BEGIN PGP MESSAGE-----' in str(result))
        self.assertTrue('-----END PGP MESSAGE-----' in str(result))
