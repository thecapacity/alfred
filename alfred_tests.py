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

    def test_index(self):
        rv = self.app.get('/')
        print rv

    def test_logout(self):
        with app.test_request_context('/logout', method='POST'):
            # now you can do something with the request until the
            # end of the with block, such as basic assertions:
            assert request.path == '/logout'
            assert request.method == 'POST'
            ## Find a way to test for no username

if __name__ == '__main__':
    unittest.main()
