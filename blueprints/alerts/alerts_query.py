"""
This module contains the queries for the alerts blueprint.
"""


def get_alerts() -> str:
    """

    Returns:

    """
    alerts_query = """
    SELECT
    ca.client_id,
    ca.topic as alert_info,
    ca.status as alert_type,
    ca.nurse_action,
    ca.code as priority,
    pt_call.last_call_date,
    COALESCE(pt_readings.days_with_readings, 0) as days_with_readings
    FROM client_alert ca
    LEFT JOIN (
    SELECT
    m.client_id,
    MAX(m.start_date_time_utc) as last_call_date
    FROM meetings m
    WHERE m.appointment_type = 'patient_call'
    or m.appointment_type = 'Patient Contact'
    or m.appointment_type is null
    GROUP BY m.client_id
    ) pt_call ON pt_call.client_id = ca.client_id
    LEFT JOIN (
    SELECT
    ckitem.client_id,
    COUNT(distinct ckrecord.created_date_time_utc) as days_with_readings
    FROM checklist_records ckrecord
    JOIN checklist_items ckitem ON ckrecord.checklist_item_id = ckitem.id
    WHERE
    ckitem.is_mandatory = 1
    AND ckitem.is_active = 1
    AND ckrecord.created_date_time_utc >= '2023-12-01'
    GROUP BY ckitem.client_id
    ) pt_readings on pt_readings.client_id = ca.client_id
    where alert_status='active' and resolved is not true;
    """

    return alerts_query


def get_alerts_by_id(user_id: str, month_to_date: str, fernet_key: str) -> str:
    """
     Notes:
    https://stackoverflow.com/questions/62417331/how-to-convert-an-integer-with-or-without-a-negative-symbol-to-a-timezone-offset
    copilot - in mysql how to convert utc to local given offset
     PT	Pacific Time	UTC -8:00 / -7:00
     MT	Mountain Time	UTC -7:00 / -6:00
     CT	Central Time	UTC -6:00 / -5:00
     ET	Eastern Time	UTC -5:00 / -4:00

     Args:
         user_id (int): nurse_id
         month_to_date (str): current month in format '2021-01-01'
         fernet_key (str):

     Returns: query
     DATE_FORMAT(CONVERT_TZ(ckrecord.created_date_time_utc, '+00:00', u.utc_timezone_offset), '%Y-%m-%d') AS created_date,

     CONCAT( IF(u.utc_timezone_offset < 0 , '-', '+'), RIGHT(CONCAT('00',LEFT(CAST(ABS(u.utc_timezone_offset) AS char(3)),1),':00'), 5))  as utc_timezone_offset

    """

    query = f"""
    SELECT DISTINCT
    CAST(AES_DECRYPT(c.name, '{fernet_key}') AS CHAR) as patient_name,
    ca.id as alert_id,  # client alert id
    ca.client_id,
    ca.topic as alert_info,
    ca.status as alert_type,
    ca.nurse_action,
    ca.code as priority,
    c.assigned_nurse_id,
    c.age,
    ca.created_at as created_at_utc,
    CAST(AES_DECRYPT(c.phone, '{fernet_key}') AS CHAR) as phone,
  #  ca.created_at,
    CONVERT_TZ(ca.created_at, '+00:00', CONCAT('-0',CAST(ABS(utc_timezone_offset) div 60 as char(1)),':00')) as created_at,
    CONCAT('-0',CAST(ABS(utc_timezone_offset) div 60 as char(1)),':00') as timezone_offset,
    ca.resolved,
    # u.utc_timezone_offset,
    pt_call.last_call_date,  # utc now but fan of users local time
    IFNULL(pt_readings.days_with_readings,0) AS days_with_readings
    FROM client_alert as ca
    JOIN clients c on ca.client_id = c.id
    JOIN users u on ca.client_id = u.id
    LEFT JOIN (
    SELECT
    m.client_id,
    MAX(m.start_date_time_utc) as last_call_date
    FROM meetings as m
    WHERE m.appointment_type in ('patient_call','Patient Contact', null)
    GROUP BY m.client_id
    )  pt_call ON pt_call.client_id = ca.client_id

    LEFT JOIN (
    SELECT
        ckitem.client_id,
#         DATE_FORMAT(ckrecord.created_date_time_utc, '%Y-%m-%d') AS created_date,
#         COUNT(DATE_FORMAT(ckrecord.created_date_time_utc, '%Y-%m-%d')) AS days_with_readings_count,
#         IF(COUNT(DATE_FORMAT(ckrecord.created_date_time_utc, '%Y-%m-%d')) > 0, 1, 0) AS days_with_readings
        DATE_FORMAT(CONVERT_TZ(ckrecord.created_date_time_utc, '+00:00', CONCAT('-0',CAST(ABS(utc_timezone_offset) div 60 as char(1)),':00')   ), '%Y-%m-%d') AS created_date,
        COUNT(DATE_FORMAT(CONVERT_TZ(ckrecord.created_date_time_utc, '+00:00',CONCAT('-0',CAST(ABS(utc_timezone_offset) div 60 as char(1)),':00')   ), '%Y-%m-%d')) AS days_with_readings_count,
        IF(COUNT(DATE_FORMAT(CONVERT_TZ(ckrecord.created_date_time_utc, '+00:00', CONCAT('-0',CAST(ABS(utc_timezone_offset) div 60 as char(1)),':00')  ), '%Y-%m-%d')) > 0, 1, 0) AS days_with_readings
    FROM checklist_records AS ckrecord
    JOIN  checklist_items AS ckitem ON ckitem.id = ckrecord.checklist_item_id
    JOIN users u on ckitem.client_id = u.id
    WHERE ckrecord.created_date_time_utc >= '{month_to_date}'
    GROUP BY client_id, created_date
    ORDER BY client_id, created_date
    ) pt_readings on pt_readings.client_id = ca.client_id
    WHERE ca.alert_status='active'
    AND c.assigned_nurse_id={user_id}
    ORDER BY ca.code ASC, ca.created_at DESC
    """
    #  WHERE ca.alert_status='active'
    #  AND ca.resolved IS NOT TRUE
    # COUNT(DISTINCT ckrecord.created_date_time_utc) as days_with_readings

    return query
