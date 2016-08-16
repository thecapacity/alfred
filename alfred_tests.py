import os
import alfred
import unittest
import tempfile

""" Guidance from: http://flask.pocoo.org/docs/0.11/testing/ """

class Alfred(unittest.TestCase):

    def setUp(self):
        self.app = alfred.app.test_client()

        with alfred.app.app_context():
            alfred.init_db()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
