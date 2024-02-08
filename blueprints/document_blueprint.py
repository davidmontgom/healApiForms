import logging

from flask import current_app, jsonify
from flask_restful import Resource
from healShared.sqlalchemy_setup.documents import models as doc_models

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PatientDocuments(Resource):
    def __init__(self):
        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")

        self.parms = parms
        self.reader = db_api["read_session"]["session"]
        self.writer = db_api["write_session"]["session"]

    def get(self, patient_id: int):
        documents = self.reader.query(doc_models.UploadedClientDocument).filter_by(client_id=patient_id).all()
        documents.sort(key=lambda document: document.display_filepath)

        return jsonify(
            status=200,
            message=[document.to_dict() for document in documents],
        )
