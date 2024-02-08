SELECT
CAST(AES_DECRYPT(c.name, 'test') AS CHAR) as patient_name,
ca.id,  # client alert id
ca.client_id,
ca.topic as alert_info,
ca.status as alert_type,
ca.nurse_action,
ca.code as priority,
ca.created_at,
c.assigned_nurse_id,
pt_call.last_call_date,
IFNULL(pt_readings.days_with_readings,0) AS days_with_readings
FROM client_alert as ca
JOIN clients c on ca.client_id = c.id

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
    DATE_FORMAT(ckrecord.created_date_time_utc, '%Y-%m-%d') AS created_date,
    COUNT(DATE_FORMAT(ckrecord.created_date_time_utc, '%Y-%m-%d')) AS days_with_readings_count,
    IF(COUNT(DATE_FORMAT(ckrecord.created_date_time_utc, '%Y-%m-%d')) > 0, 1, 0) AS days_with_readings
FROM checklist_records AS ckrecord
JOIN  checklist_items AS ckitem ON ckitem.id = ckrecord.checklist_item_id
WHERE ckrecord.created_date_time_utc >= '2023-12-01'
GROUP BY client_id, created_date
ORDER BY client_id, created_date
) pt_readings on pt_readings.client_id = ca.client_id

WHERE ca.alert_status='active'
AND ca.resolved IS NOT TRUE
