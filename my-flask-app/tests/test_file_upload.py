import unittest
from app.api.document_routes import create_app
from flask import request
from werkzeug.datastructures import FileStorage
import os
from werkzeug.test import EnvironBuilder
from flask.wrappers import Request

class TestFileUpload(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()

    def test_file_upload(self):
        with open('tests/test.pdf', 'rb') as fp:
            response = self.client.post(
                '/api/process',
                data={
                    'document_type': '1040',
                    'file': (fp, 'test.pdf')
                }
            )
        print(response.data)  # Print the response data
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()