import os
import sys
import unittest
import uuid
from unittest.mock import patch

import boto3
import moto

sys.path.append(".")
sys.path.append("..")
sys.path.append("../../healShared")
sys.path.append("../blueprints")
sys.path.append("../healApiPractice")
from healApiPractice.blueprints.nurse_users import NurseObject

print(os.environ.get("REGION"))
parms = {
    "slug": "heal",
    "environment": "local",
    "region": "us-east-1",
    "location": "us-east-1",  # os.environ.get("REGION").replace("-", ""),
    "cognito_meta": {
        "pool_id": "test",
        "client_id": "test",
        "secret_id": "test",
    },
    "AWS_ACCESS_KEY_ID": "testing",
    "AWS_SECRET_ACCESS_KEY": "testing",
    "AWS_SECURITY_TOKEN": "testing",
    "AWS_SESSION_TOKEN": "testing",
}


@moto.mock_cognitoidp
class TestNurseObject(unittest.TestCase):
    @classmethod
    @moto.mock_cognitoidp
    def setUpClass(cls):
        """
        Notes:
            Ideally we want to create the user pool here but not working yet.

        Returns:
            None

        """

        # https://github.com/getmoto/moto/blob/master/tests/test_cognitoidp/test_cognitoidp.py
        conn = boto3.client(
            "cognito-idp",
            aws_access_key_id=parms["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=parms["AWS_SECRET_ACCESS_KEY"],
            aws_session_token=parms["AWS_SESSION_TOKEN"],
            region_name="us-east-1",
        )
        name = str(uuid.uuid4())
        value = str(uuid.uuid4())
        result = conn.create_user_pool(PoolName=name, LambdaConfig={"PreSignUp": value})
        cls.pool_id = result["UserPool"]["Id"]

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.parms = parms

        self.db_api = {
            "reader": None,
            "writer": None,
        }

    def tearDown(self):
        pass

    def test_a_create_cognito_nurse_user(self):
        """
        Notes:
            Test creating a cognito user using moto.
        Returns:

        """

        # We need to create a mock user pool
        conn = boto3.client(
            "cognito-idp",
            aws_access_key_id=parms["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=parms["AWS_SECRET_ACCESS_KEY"],
            aws_session_token=parms["AWS_SESSION_TOKEN"],
            region_name="us-east-1",
        )
        name = str(uuid.uuid4())
        value = str(uuid.uuid4())
        result = conn.create_user_pool(PoolName=name, LambdaConfig={"PreSignUp": value})
        pool_id = result["UserPool"]["Id"]
        self.__class__.pool_id = pool_id
        self.parms["cognito_meta"]["pool_id"] = pool_id

        data = {
            "email": "test@gmail.com",
            "username": "test@gmail.com",
        }

        no = NurseObject(self.parms, self.db_api)
        res = no.create_cognito_user(data)

        self.assertEqual(res["status_code"], 200)

    @patch.object(NurseObject, "insert_nurse_user_into_db")
    def test_b_insert_nurse_user_into_db(self, insert_nurse_user_into_db_method):
        """
        Notes: For not we will mock inserts until we have a test db.

        Returns:

        """

        data = {
            "email": "test@gmail.com",
            "username": "test",
        }

        insert_nurse_user_into_db_method.return_value = True

        no = NurseObject(self.parms, self.db_api)
        res = no.insert_nurse_user_into_db(data)

        self.assertEqual(res, True)


if __name__ == "__main__":
    # python3 -m unittest test_nurse.py -v
    unittest.main(failfast=True, exit=False)
