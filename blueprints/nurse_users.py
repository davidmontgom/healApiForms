"""Endpoint for NURSE_USERS CRUD operations."""

import logging
import sys

from flask import current_app, jsonify, request
from flask_restful import Resource

sys.path.append("../../healShared")
from healShared.cognito_tools import cognito_object

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class NurseUser(Resource):

    """
    NurseUser class for CRUD operations.
    """

    def get(self, nurse_id: str):
        """

        Args:
            nurse_id ():

        Returns:

        """
        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")
        logger.info(parms)
        logger.info(db_api)

        return jsonify(status=200, message={"id": nurse_id, "score": "0"})

    def post(self):
        """

        Returns:

        """
        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")
        data = request.get_json(force=True)
        logger.info(parms)

        no = NurseObject(parms=parms, db_api=db_api)
        res = no.create_nurse_user(data)
        # = no.insert_nurse_user_into_db(data)
        logger.info(res)

        return jsonify(status=200, message={"message": "user created"})


class NurseUsers(Resource):

    """
    NurseUsers class for CRUD operations.
    """

    def get(self):
        """

        Returns:

        """

        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")
        logger.info(parms)
        logger.info(db_api)

        meta = {"foo": "bar"}

        return jsonify(status=200, message=meta)


class NurseObject:

    """
    NurseObject class for CRUD operations.
    """

    def __init__(self, parms: dict, db_api: dict) -> None:
        """

        Args:
            parms ():
            db_api ():
        """

        self.parms = parms
        self.reader = db_api["reader"]
        self.writer = db_api["writer"]
        logger.info(parms)

    def create_cognito_user(self, data: dict) -> dict:
        """

        Args:
            data (dict): User data to create a cognito user.

        Returns:

        """
        cognito_meta = self.parms["cognito_meta"]

        username = data["email"]
        email = data["email"]
        group = None
        if "group" in data:
            group = data["group"]

        co = cognito_object(data=None, parms=self.parms, cognito_meta=cognito_meta, region="us-west-2")
        res = co.admin_create_user(username, email, resend=False)
        logger.info(res)

        if group is not None:
            res_group = co.admin_add_user_to_group(username, group)
            logger.info("res_group: %s", res_group)

        # TODO THIS IS WHERE WE INIT THE USER DATABASE.  WE CANT DO IT IN THE COGNITO TRIGGER FOR ADMIN CREATE USER

        return res

    def insert_nurse_user_into_db(self, data: dict) -> bool:
        """

        Args:
            data (dict): User data to insert into the database.

        Returns:

        """
        logger.info(data)
        query = "SELECT now()"
        res = self.reader.execute_query(query, select=True)
        logger.info(res)

        return True

    def create_nurse_user(self, data: dict) -> int:
        """

        Args:
            data (dict):

        Returns:

        """

        self.create_cognito_user(data)
        self.insert_nurse_user_into_db(data)

        return 201
