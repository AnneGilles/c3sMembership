import unittest
import subprocess

from c3smembership import scripts # just to trigger coverage
#from c3smembership.scripts.initialize_db import init_50


class TestDBInitialization(unittest.TestCase):
    """
    tests for the database initialization scripts
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_usage(self):
        from c3smembership.scripts.initialize_db import usage
        argv = ['initialize_c3sMembership_db']
        try:  # we will hit SystemExit: 1
            result = usage(argv)
            print("the result: %s" % result)
        except:
            #print ("caught exception!")
            pass
    # def test_usage_process(self):
    #     try:
    #         res = subprocess.check_output(
    #             ['env/bin/initialize_c3sMembership_db'])
    #         #print res
    #     except subprocess.CalledProcessError, cpe:
    #         #print("return code: %s" % cpe.returncode)
    #         #print("output: %s" % cpe.output)
    #         self.assertTrue(cpe.returncode is 1)
    #         self.assertTrue(
    #             'usage: initialize_c3sMembership_db <config_uri>' in cpe.output
    #         )

#    def test_init(self):
#        from c3smembership.scripts.initialize_db import init
#

    def test_main(self):
        from c3smembership.scripts.initialize_db import main
        # get it wrong: wrong number of arguments
        try:
            argv = ['foo', ]
            result = main(argv)
        #    print("the result: %s" % result)
        except:
            #print ("caught exception!")
            pass
        # get it right: two arguments
        try:
            argv = ['initialize_c3sMembership_db', 'development.ini']
            result = main(argv)
            print("the result: %s" % result)
        except:
            print ("caught exception!")
