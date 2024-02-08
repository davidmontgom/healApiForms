"""
This is the entry point for the flask app. It is used by the serverless framework to start the flask app.
"""
from gevent import monkey
import os
monkey.patch_all()
import logging
import os
import sys

import redis
from flask import Flask
from flask_cors import CORS
from sqlalchemy.orm import configure_mappers

sys.path.append("..")
sys.path.append("../healShared")
from healShared.pymysql_tools import PyMysqlObject
from healShared.sqlalchemy_connection_tools import get_connection_obj
from healShared.sqlalchemy_setup.setup import get_mysql_sqlalchemy_handhers

from healApiPractice.app_blueprint import get_resource

if __name__ == "__main__":
    import os
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.info("Starting serverless flask app")

    db_host = os.environ.get("DB_HOST")
    db_username = os.environ.get("DB_USERNAME")
    db_password = os.environ.get("DB_PASSWORD")
    db_api_database = os.environ.get("DB_API_DATABASE")
    db_port = int(os.environ.get("DB_PORT"))

    # CREATE LOCAL HOST DATABASE CONNECTIONS FOR READ AND WRITE
    db_api_writer = PyMysqlObject(db_host, db_username, db_password, db_api_database, port=db_port)
    db_api_reader = PyMysqlObject(db_host, db_username, db_password, db_api_database, port=db_port)

    # CREATE SQLALCHEMY CONNECTIONS FOR READ AND WRITE
    fernet_key = os.environ.get("FERNET_KEY")
    __engine_map_reader = get_connection_obj(db_username, db_password, db_host, db_port, db_api_database, fernet_key)
    __engine_map_writer = get_connection_obj(db_password, db_password, db_host, db_port, db_api_database, fernet_key)

    # CREATE REDIS CONNECTIONS FOR READ AND WRITE
    redis_reader = redis.StrictRedis()
    redis_writer = redis.StrictRedis()

    db_api = {
        "writer": db_api_writer,
        "reader": db_api_reader,
        "redis_reader": redis_reader,
        "redis_writer": redis_writer,
        "__engine_map_reader": __engine_map_reader,
        "__engine_map_writer": __engine_map_writer,
        "read_session": get_mysql_sqlalchemy_handhers(
            db_username,
            db_password,
            db_host,
            db_port,
            db_api_database,
            fernet_key,
        ),
        "write_session": get_mysql_sqlalchemy_handhers(
            db_username,
            db_password,
            db_host,
            db_port,
            db_api_database,
            fernet_key,
        ),
    }

    parms = {
        "slug": os.environ.get("SLUG"),
        "environment": os.environ.get("ENVIRONMENT"),
        "region": os.environ.get("REGION"),
        "location": os.environ.get("REGION").replace("-", ""),
        "FERNET_KEY": os.environ.get("FERNET_KEY"),
        "MAX_PAGE_SIZE": os.environ.get("MAX_PAGE_SIZE"),
        "cognito_meta": {
            "pool_id": os.environ.get("PRACTICE_COGNITO_USER_POOL_ID"),
            "client_id": os.environ.get("PRACTICE_COGNITO_CLIENT_ID"),
            "secret_id": os.environ.get("PRACTICE_COGNITO_CLIENT_SECRET"),
        },
    }

    configure_mappers()
    app = Flask(__name__)
    CORS(app)
    app.config["db_api"] = db_api
    app.config["parms"] = parms

    # add blueprints with flask_restful
    app = get_resource(app)
    app.run(debug=True, host="0.0.0.0", port=8050)
