import itertools
import logging
from datetime import datetime
import os
from healShared.date_tools import convert_dt_object_to_dt_str

from healApiPractice.blueprints.alerts.alerts_query import get_alerts, get_alerts_by_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AlertObject:
    def __init__(self, parms: dict, db_api: dict) -> None:
        """

        Args:
                parms ():
                db_api ():
        """

        self.params = parms
        self.db_api = db_api
        self.reader = db_api["reader"]
        self.writer = db_api["writer"]

    def get_alerts(self) -> dict:
        query = get_alerts()
        data = self.reader.execute_query(query, select=True)

        meta = []
        if data:
            for idx in data:
                if idx["last_call_date"]:
                    last_call_date = idx["last_call_date"].strftime("%Y-%m-%dT%H:%M:%S")
                    idx["last_call_date"] = last_call_date
                meta.append(idx)

        return meta

    def get_alerts_by_user(self, user_id: str) -> dict:
        """

        Args:
                user_id ():

        Returns:

        """
        month_to_date = convert_dt_object_to_dt_str(datetime.utcnow(), fmt="%Y-%m-01")

        year = datetime.utcnow().year
        month = datetime.utcnow().month
        fernet_key = self.params["FERNET_KEY"]

        query = get_alerts_by_id(user_id, month_to_date, fernet_key)
        data = self.reader.execute_query(query, select=True)

        # NOTES: THIS IS AS MESS BUT ITS A FIRST PASS FOR CALCULATING CUMULATIVE DAYS WITH READINGS
        # FOR THE CURRENT MONTH.  WE WILL REFACTOR LATER TO BE MORE EFFICIENT AND CLEANER
        # ONLY THE CURRENT MONTH IS CALCULATED FOR NOW
        final_hash = {}
        if data:
            date_hash = {}
            # create a list of dates with readings per client
            for i, idx in enumerate(data):
                if (
                    idx["created_at"].year == year
                    and idx["created_at"].month == month
                    and idx["days_with_readings"] == 1
                ):
                    client_id = idx["client_id"]
                    dt_str = convert_dt_object_to_dt_str(idx["created_at"], fmt="%Y-%m-%d")
                    if client_id not in date_hash:
                        date_hash[client_id] = [dt_str]
                    else:
                        if dt_str not in date_hash[client_id]:
                            date_hash[client_id].append(dt_str)

            # Once we create the list of dates with readings per clients this is where we
            # calculate the cumulative counts
            final_hash = {}
            for client_id, date_list in date_hash.items():
                reading_count_list = [1] * len(date_list)
                res = list(itertools.accumulate(reading_count_list))
                res = {date_list[i]: res[i] for i in range(len(date_list))}
                final_hash[client_id] = res

        meta = []
        if data:
            for i, idx in enumerate(data):
                if (
                    idx["created_at"].year == year
                    and idx["created_at"].month == month
                    and idx["days_with_readings"] == 1
                ):
                    created_at_str = idx["created_at"].strftime("%Y-%m-%d")
                    client_id = idx["client_id"]
                    if client_id in final_hash and created_at_str in final_hash[client_id]:
                        idx["days_with_readings"] = final_hash[client_id][created_at_str]  # cumm value
                if idx["last_call_date"]:
                    last_call_date = idx["last_call_date"].strftime("%Y-%m-%dT%H:%M:%SZ")
                    idx["last_call_date"] = last_call_date
                else:
                    idx["last_call_date"] = None
                if idx["created_at"]:
                    created_at = idx["created_at"].strftime("%Y-%m-%dT%H:%M:%S")
                    idx["created_at"] = created_at
                if idx["created_at_utc"]:
                    created_at_utc = idx["created_at_utc"].strftime("%Y-%m-%dT%H:%M:%SZ") # Z browser with auto convert to local time with date pipe
                    idx["created_at_utc"] = created_at_utc
                else:
                    idx["created_at"] = None
                # if idx["days_with_readings"] is None:
                #     idx["days_with_readings"] = 0
                # idx["index"] = i

                if idx["resolved"] == 0 and idx["priority"] in ["critical", "high"]:  # ca.resolved IS NOT TRUE
                    del idx["resolved"]
                    if idx["priority"] == "high":
                        idx["priority_ord"] = 9
                    elif idx["priority"] == "critical":
                        idx["priority_ord"] = 10
                    meta.append(idx)

        return meta

    def resolve_alert(self, alert_id: int) -> dict:
        """

        Args:
                alert_id ():

        Returns:

        """
        query = (
            f"""UPDATE client_alert SET alert_status = "resolved", resolved = True WHERE client_alert.id = {alert_id}"""
        )
        data = self.writer.execute_query(query, select=False)
        logging.info(data)

        return data



if __name__ == "__main__":
    import os
    from pprint import pprint

    from healShared.pymysql_tools import PyMysqlObject, rds_object

    parms = {
        "region": os.environ.get("REGION"),
        "slug": os.environ.get("SLUG"),
        "location": os.environ.get("LOCATION"),
        "environment": os.environ.get("ENVIRONMENT"),
        "FERNET_KEY": os.environ.get("FERNET_KEY"),
    }

    print(parms)

    db_host_writer = os.environ.get("DB_HOST")
    db_host_reader = os.environ.get("DB_HOST")
    db_port = int(os.environ.get("DB_PORT"))
    db_iam_username = os.environ.get("DB_USERNAME")
    db_password = os.environ.get("DB_PASSWORD")
    db_api_database = os.environ.get("DB_API_DATABASE")
    use_proxy = False

    print(db_host_writer, db_host_reader, db_port, db_iam_username, db_password, db_api_database)

    db_api_writer = PyMysqlObject(
        db_host_writer, db_iam_username, db_password, db_api_database, port=db_port, use_proxy=use_proxy
    )
    db_api_reader = PyMysqlObject(
        db_host_reader, db_iam_username, db_password, db_api_database, port=db_port, use_proxy=use_proxy
    )

    db_api = {
        "writer": db_api_writer,
        "reader": db_api_reader,
        # "__engine_map_reader": __engine_map_reader,
        # "__engine_map_writer": __engine_map_writer,
        # "redis_reader": redis_reader,
        # "redis_writer": redis_writer,
    }

    at = AlertObject(parms, db_api)
    user_id = 2365  # prod
    user_id = 2477  # dev
    # user_id = 2844 # bad dev
    res = at.get_alerts_by_user(user_id)
    pprint(res)
