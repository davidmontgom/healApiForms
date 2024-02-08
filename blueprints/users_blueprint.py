import logging

from flask import current_app, jsonify
from flask_restful import Resource

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Users(Resource):

    """
    NurseUsers class for CRUD operations.
    """

    def get(self):
        """

        Returns:

        """

        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")

        ut = UserObject(parms, db_api)
        meta = ut.get_users()

        return jsonify(status=200, message=meta)


class UserObject:

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

    def get_users(self) -> dict:
        fernet = self.parms["FERNET_KEY"]
        query = f"""
        SELECT u.id,
        CAST(AES_DECRYPT(u.name, '{fernet}') AS CHAR) AS name,
        CAST(AES_DECRYPT(u.email, '{fernet}') AS CHAR) AS email
        FROM users u
        JOIN user_to_role_and_hospital utrh ON u.id = utrh.user_id
        JOIN roles r ON utrh.role_id = r.id
        WHERE u.is_archived = 0
        AND  r.name = 'nurse'
        AND u.email IS NOT NULL
        AND u.name IS NOT NULL
        AND (
        u.last_login_activity >= '2021-06-07 11:49:29.292261'
        OR
        u.nurse_invitation_code IS NOT NULL
        )
        GROUP BY u.id, u.name, u.email
        ORDER BY u.name
        """
        print(query)

        data = self.reader.execute_query(query, select=True)

        meta = []
        if data:
            for row in data:
                meta.append(
                    {
                        "user_id": row["id"],
                        "name": row["name"],
                        "email": row["email"],
                    }
                )

        return meta

    def get_user(self, email=None, user_id=None) -> list:
        fernet = self.parms["FERNET_KEY"]

        query = f"""SELECT u.id, CAST(AES_DECRYPT(u.email, '{fernet}') AS CHAR) AS email FROM users as u WHERE
        CAST(AES_DECRYPT(u.email, '{fernet}') AS CHAR)  = '{email}'"""

        data = self.reader.execute_query(query, select=True)
        meta = []
        if data:
            for row in data:
                meta.append(
                    {
                        "user_id": row["id"],
                        "name": row["name"],
                        "email": row["email"],
                    }
                )

        return meta


#
#
# if __name__ == "__main__":
#     import os
#     import sys
#
#     sys.path.append("..")
#     sys.path.append("../healShared")
#     from healShared.pymysql_tools import PyMysqlObject
#
#     db_host = os.environ.get("DB_HOST")
#     db_username = os.environ.get("DB_USERNAME")
#     db_password = os.environ.get("DB_PASSWORD")
#     db_api_database = os.environ.get("DB_API_DATABASE")
#     db_port = int(os.environ.get("DB_PORT"))
#
#     # CREATE LOCAL HOST DATABASE CONNECTIONS FOR READ AND WRITE
#     db_api_writer = PyMysqlObject(db_host, db_username, db_password, db_api_database, port=db_port)
#     db_api_reader = PyMysqlObject(db_host, db_username, db_password, db_api_database, port=db_port)
#
#     # # CREATE SQLALCHEMY CONNECTIONS FOR READ AND WRITE
#     # __engine_map_reader = get_mysql_sqlalchemy_handhers(db_username, db_password, db_host, db_port, db_api_database)
#     # __engine_map_writer = get_mysql_sqlalchemy_handhers(db_password, db_password, db_host, db_port, db_api_database)
#     #
#     # # CREATE REDIS CONNECTIONS FOR READ AND WRITE
#     # redis_reader = redis.StrictRedis()
#     # redis_writer = redis.StrictRedis()
#
#     db_api = {
#         "writer": db_api_writer,
#         "reader": db_api_reader,
#         # "redis_reader": redis_reader,
#         # "redis_writer": redis_writer,
#         # "__engine_map_reader": __engine_map_reader,
#         # "__engine_map_writer": __engine_map_writer,
#     }
#
#     parms = {
#         "slug": os.environ.get("SLUG"),
#         "environment": os.environ.get("ENVIRONMENT"),
#         "region": os.environ.get("REGION"),
#         "location": os.environ.get("REGION").replace("-", ""),
#         "FERNET_KEY": os.environ.get("FERNET_KEY"),
#         "cognito_meta": {
#             "pool_id": os.environ.get("PRACTICE_COGNITO_USER_POOL_ID"),
#             "client_id": os.environ.get("PRACTICE_COGNITO_CLIENT_ID"),
#             "secret_id": os.environ.get("PRACTICE_COGNITO_CLIENT_SECRET"),
#         },
#     }
#
#     ut = UserObject(parms, db_api)
#     ut.get_users()
#     res = ut.get_user(email="katherinejordan@myyahoo.com")
#     print(res)
