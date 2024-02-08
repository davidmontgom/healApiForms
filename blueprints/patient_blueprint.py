import logging

from flask import abort, current_app, jsonify, request
from flask_restful import Resource
from healShared.sqlalchemy_setup.assesment import models as assessment_models
from healShared.sqlalchemy_setup.care_protocol import models as cp_models
from healShared.sqlalchemy_setup.clients import models as client_models
from healShared.sqlalchemy_setup.clients.views.api_nurse import (
    get_clients_query,
    x__client_to_dict,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Patient(Resource):
    def __init__(self):
        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")

        self.parms = parms
        self.reader = db_api["read_session"]["session"]
        self.writer = db_api["write_session"]["session"]

    def get(self, patient_id: int):
        client = (
            get_clients_query(
                self.reader,
                True,
                [
                    [client_models.Client.care_protocol, cp_models.CareProtocol.assesments],
                    [
                        client_models.Client.care_protocol,
                        cp_models.CareProtocol.assesments,
                        assessment_models.CareProtocolAssesment.assesment,
                    ],
                    [client_models.Client.user],
                    [client_models.Client.nurses],
                    [client_models.Client.assigned_nurse],
                    [client_models.Client.diagnoses],
                    [client_models.Client.diagnoses, client_models.ClientDiagnose.diagnose],
                    [
                        client_models.Client.diagnoses,
                        client_models.ClientDiagnose.diagnose,
                        client_models.Diagnose.category,
                    ],
                ],
            )
            .filter_by(id=patient_id)
            .first()
        )
        if not client:
            return abort(404)
        response = x__client_to_dict(
            self.reader,
            client,
            start_datetime=request.args.get("start-datetime"),
            end_datetime=request.args.get("end-datetime"),
        )
        response["hif_progress"] = client.get_healent_index_function_progress(self.reader, as_dict=True)
        return jsonify(status=200, message=response)


class PatientNotes(Resource):
    def __init__(self):
        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")

        self.parms = parms
        self.reader = db_api["read_session"]["session"]
        self.writer = db_api["write_session"]["session"]

    def get(self, patient_id: int):
        client = self.reader.query(client_models.Client).filter_by(id=patient_id).first()
        (client.communication_entries or []).sort(key=lambda x: x["date"], reverse=True)

        return jsonify(
            status=200,
            message=client.communication_entries,
        )
