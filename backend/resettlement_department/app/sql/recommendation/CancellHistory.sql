WITH params AS (
    SELECT (:history_id)::integer AS history_id_param 
),
delete_offers AS (
    DELETE FROM offer
    WHERE affair_id IN (
        SELECT affair_id FROM old_apart 
        WHERE history_id = (SELECT history_id_param FROM params)
    )
),
update_old_aparts AS (
    UPDATE old_apart  
    SET history_id = NULL,
        rank = NULL
    WHERE history_id = (SELECT history_id_param FROM params)
),
update_new_aparts AS (
    UPDATE new_apart 
    SET history_id = NULL,
        rank = NULL
    WHERE history_id = (SELECT history_id_param FROM params)
),
delete_history AS (
    DELETE FROM history 
    WHERE history_id = (SELECT history_id_param FROM params)
)
SELECT 'done' AS status;  