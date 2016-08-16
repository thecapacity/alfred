import os
import alfred
import unittest
import tempfile

""" Guidance from: http://flask.pocoo.org/docs/0.11/testing/#testing """

class Alfred(unittest.TestCase):

    """ Look here for more information: http://flask.pocoo.org/docs/0.11/testing/ """

    def setUp(self):
        self.app = alfred.app.test_client()

        with alfred.app.app_context():
            alfred.init_db()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
