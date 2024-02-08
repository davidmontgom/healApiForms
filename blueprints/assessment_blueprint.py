import logging

from flask import current_app, jsonify
from flask_restful import Resource
from healShared.sqlalchemy_setup.assesment import models as assessment_models
from healShared.sqlalchemy_setup.clients import models as client_models
from healShared.sqlalchemy_setup.microprotocols import models as microprotocol_models

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PatientIntakeAssessments(Resource):
    def __init__(self):
        parms = current_app.config.get("parms")
        db_api = current_app.config.get("db_api")

        self.parms = parms
        self.reader = db_api["read_session"]["session"]
        self.writer = db_api["write_session"]["session"]

    def get(self, patient_id: int):
        client = self.reader.query(client_models.Client).filter_by(id=patient_id).first()

        rpm_rtm = None
        risk = None
        health_risk = None

        if client.monitoring_program != "CCM":
            risk_assessment = assessment_models.RiskAssessment.get_risk_assessment(self.reader, client)
            risk_submit_date = risk_assessment.submitted_on if risk_assessment else None

            rpm_rtm_assessment = assessment_models.RTMRPMAssessment.get_rtm_rpm_assessment(self.reader, client)
            rpm_submit_date = rpm_rtm_assessment.submitted_on if rpm_rtm_assessment else None

            rpm_rtm = (
                {
                    "id": rpm_rtm_assessment.id,
                    "submitted_on_fulldatetime": rpm_submit_date,
                    "submitted_on": rpm_submit_date.date(),
                    "survey_answers": rpm_rtm_assessment.answers,
                }
                if rpm_rtm_assessment
                else None
            )

            risk = (
                {
                    "id": risk_assessment.id,
                    "medd_value": risk_assessment.medd_value,
                    "osord_value": risk_assessment.osord_value,
                    "submitted_on_fulldatetime": risk_submit_date,
                    "submitted_on": risk_submit_date.date(),
                    "survey_answers": risk_assessment.answers,
                }
                if risk_assessment
                else None
            )
        else:
            questions_submit = (
                self.reader.query(microprotocol_models.QuestionsSubmit)
                .filter(microprotocol_models.QuestionsSubmit.client_id == client.id)
                .first()
            )
            submitted_at = (
                client.user.from_utc_to_user(questions_submit.updated_at or questions_submit.created_at)
                if questions_submit
                else None
            )

            health_risk = (
                {
                    "id": questions_submit.id,
                    "score": questions_submit.score,
                    "submitted_on": submitted_at.strftime("%Y-%m-%d") if submitted_at else None,
                }
                if questions_submit
                else None
            )

        return jsonify(
            status=200,
            message={"rpm_rtm_assessment": rpm_rtm, "risk_assessment": risk, "health_risk_assessment": health_risk},
        )
