"""
Blueprints are a way to organize related views and other code.  They are registered with the Flask app object
"""

from flask import Blueprint
from flask_restful import Api

from healApiForms.blueprints.forms.forms_blueprint import FormsResource


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


    ##########################################
    # FORMS
    ##########################################
    api.add_resource(FormsResource, "/form/hmsa")

    app.register_blueprint(api_bp)

    return app
