"""
Blueprints are a way to organize related views and other code.  They are registered with the Flask app object
"""

from flask import Blueprint
from flask_restful import Api

from healApiPractice.blueprints.alerts.alerts_blueprint import (
    AlertResolveResource,
    AlertResource,
    AlertsResource,
)
from healApiPractice.blueprints.assessment_blueprint import PatientIntakeAssessments
from healApiPractice.blueprints.care_protocol_blueprint import PatientSurgeryInfos
from healApiPractice.blueprints.document_blueprint import PatientDocuments
from healApiPractice.blueprints.nurse_users import NurseUser  # , NurseUsers
from healApiPractice.blueprints.nurses.nurses_blueprint import NursesResource
from healApiPractice.blueprints.patient_blueprint import Patient, PatientNotes
from healApiPractice.blueprints.users_blueprint import Users


def get_resource(app):
    """
    Notes:
            Registers the api resource with the Flask app object.  This is a combination of the Flask Blueprints
            and the Flask-RESTful Api object

    Args:
            app (object): The Flask app object

    Returns:
            object: The Flask app object with the api resource added

    """

    api_bp = Blueprint("api", __name__)
    api = Api(api_bp)

    api.add_resource(NursesResource, "/nurses")
    api.add_resource(NurseUser, "/nurseuser/<int:id>", "/nurseuser")

    api.add_resource(Users, "/users", "/users")

    ##########################################
    # ALERTS
    ##########################################
    api.add_resource(AlertsResource, "/alerts")
    api.add_resource(AlertResource, "/alerts/<int:user_id>")
    api.add_resource(AlertResolveResource, "/alerts/resolve/<int:user_id>/<int:alert_id>")

    ##########################################
    # PATIENTS
    ##########################################
    api.add_resource(Patient, "/patient/<int:patient_id>")
    api.add_resource(PatientNotes, "/patient/<int:patient_id>/notes")

    ##########################################
    # CARE_PROTOCOL
    ##########################################
    api.add_resource(PatientSurgeryInfos, "/patient/<int:patient_id>/surgery-infos")

    ##########################################
    # ASSESSMENT
    ##########################################
    api.add_resource(PatientIntakeAssessments, "/patient/<int:patient_id>/intake-assessments")

    ##########################################
    # DOCUMENT
    ##########################################
    api.add_resource(PatientDocuments, "/patient/<int:patient_id>/documents")

    app.register_blueprint(api_bp)

    return app
