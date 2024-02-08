"""
NURSES ENDPOINT
"""
import logging

from flask import current_app, jsonify
from flask_restful import Resource

from healApiPractice.blueprints.alerts.alert_tools import AlertObject

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AlertsResource(Resource):

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

        try:
            ut = AlertObject(parms, db_api)
            meta = ut.get_alerts()
        except Exception as e:
            # we will add sentry capture exception here and expand exception handling
            logger.error(e)
            return jsonify(status=500, message="Internal Server Error")

        return jsonify(status=200, message=meta)


class AlertResource(Resource):
    """
    Notes: Endpoint to get a single nurse
    """

    def get(self, user_id: str):
        """
        Notes: Endpoint to get a single nurse

        Args:
            nurse_id (str): nurse_id

        Returns:
            Json response of nurse
        """

        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")

        try:
            ut = AlertObject(parms, db_api)
            meta = ut.get_alerts_by_user(user_id)
        except Exception as e:
            # we will add sentry capture exception here and expand exception handling
            logger.error(e)
            return jsonify(status=500, message="Internal Server Error")

        return jsonify(status=200, message=meta)


class AlertResolveResource(Resource):
    """
    Notes: Endpoint to get a single nurse
    """

    def get(self, user_id: int, alert_id: int):
        """
        Notes: Endpoint to get a single nurse.  user_id is not used but is required for the route.  Later will be
        used as a sanity check to make sure the user is authorized to resolve the alert.  Might be the case that
        a manager can resolve an alert for a nurse.

        Args:
            user_id (str): user_id
            alert_id (str): alert_id

        Returns:
            Json response of nurse
        """

        logger.info(f"alert_id: {alert_id}")
        logger.info(f"user_id: {user_id}")

        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")

        try:
            ut = AlertObject(parms, db_api)
            meta = ut.resolve_alert(alert_id)
        except Exception as e:
            # we will add sentry capture exception here and expand exception handling
            logger.error(e)
            return jsonify(status=500, message="Internal Server Error")

        return jsonify(status=200, message=meta)
