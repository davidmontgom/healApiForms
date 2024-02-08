"""
NURSES ENDPOINT
"""
import logging
from flask import current_app, jsonify, request
from flask_restful import Resource

from healApiForms.blueprints.forms.forms_tools import FormsObject

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FormsResource(Resource):

    """
    Notes: Endpoint to get all nurses
    """

    def get(self):
        """

        Notes: Endpoint to get all nurses

        Returns:
            Json response of nusres

        """

        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")

        # search = request.args.get("search")
        # page = request.args.get("page")  # convert to int
        # page_size = request.args.get("page_size")  # convert to int

        try:
            nt = FormsObject(parms, db_api)
            meta = nt.get_forms()
            print("meta", meta)
        except Exception as e:
            # we will add sentry capture exception here and expand exception handling
            logger.error(e)
            return jsonify(status=500, message="Internal Server Error")

        # CAN USE PYDANTIC TO VALIDATE THE RESPONSE DATA OR MARSHMALLOW IF BEST PRACTICE
        return jsonify(status=200, message=meta)
