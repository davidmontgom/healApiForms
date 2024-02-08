"""
Flask unit tests for the nurse API
"""

import json
import os
import sys
import unittest

from flask import Flask

# unittest.TestLoader.sortTestMethodsUsing = None

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../healApiPractice")

from healApi.app_blueprint import get_blueprint, get_resource
from healShared.pymysql_tools import PyMysqlObject


class TestNurseFlaskObject(unittest.TestCase):

    """
    Adjust the resources and the database tables required for the tests
    """

    @classmethod
    def setUpClass(cls):
        """

        Returns:

        """
        #####################################################################
        # ADD ONLY IMPORTS REQUIRED FOR UNIT TESTS BELOW THIS LINE
        #####################################################################
        db_host = os.environ.get("DB_HOST")
        db_username = os.environ.get("DB_USERNAME")
        db_password = os.environ.get("DB_PASSWORD")
        db_api_database = os.environ.get("DB_API_DATABASE")
        db_port = int(os.environ.get("DB_PORT"))

        parms = {
            "slug": os.environ.get("SLUG"),
            "environment": os.environ.get("ENVIRONMENT"),
            "region": os.environ.get("REGION"),
            "location": os.environ.get("REGION").replace("-", ""),
            "cognito_meta": {
                "pool_id": os.environ.get("COGNITO_USER_POOL_ID"),
                "client_id": os.environ.get("COGNITO_CLIENT_ID"),
                "secret_id": os.environ.get("COGNITO_CLIENT_SECRET"),
            },
        }

        db_api_writer = PyMysqlObject(db_host, db_username, db_password, db_api_database, port=db_port)
        db_api_reader = PyMysqlObject(db_host, db_username, db_password, db_api_database, port=db_port)
        db_api = {"writer": db_api_writer, "reader": db_api_reader}
        app = Flask(__name__)
        app.config["db_api"] = db_api
        app.config["parms"] = parms
        # add blueprints
        app = get_blueprint(app)
        # add blueprints with flask_restful
        cls.app = get_resource(app)

    @classmethod
    def tearDownClass(cls):
        """
        Remove the resources and the database tables required for the tests
        Returns:

        """

    def setUp(self):
        """
        Setup the flask app for testing
        Returns:

        """
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        """
        Remove the flask app for testing
        Returns:

        """
        self.ctx.pop()

    def test_b_get_nurses(self):
        """
        Test the get nurses endpoint
        Returns:

        """
        rv = self.client.get("/serverless/todos")
        res = rv.data.decode()
        res = json.loads(res)
        print(res)
        self.assertEqual(res["status"], 200)


if __name__ == "__main__":
    # python3 -m unittest test_flask_api_nurse.py -v

    unittest.main(failfast=True, exit=False)
    # unittest.main()
    sys.exit()
