import logging

from flask import current_app, jsonify
from flask_pydantic import validate
from flask_restful import Resource
from healShared.sqlalchemy_setup.care_protocol import models as cp_models
from healShared.sqlalchemy_setup.care_protocol.schema import SurgeryInfoQueryModel
from healShared.sqlalchemy_setup.common.pagination import pagination_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PatientSurgeryInfos(Resource):
    def __init__(self):
        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")

        self.parms = parms
        self.reader = db_api["read_session"]["session"]
        self.writer = db_api["write_session"]["session"]

    @validate()
    def get(self, patient_id: int, query: SurgeryInfoQueryModel):
        db_query = self.reader.query(cp_models.SurgeryInfo).filter(cp_models.SurgeryInfo.client_id == patient_id)
        data, total = pagination_response(
            db_query=db_query,
            model=cp_models.SurgeryInfo,
            query=query,
        )
        return jsonify(
            status=200, message={"data": [d.to_dict() for d in data], "recordsFiltered": total, "recordsTotal": total}
        )
