WITH params AS (
    SELECT (:manual_load_id)::integer AS manual_load_param 
),
delete_offers AS (
    DELETE FROM offer
    WHERE affair_id IN (
        SELECT affair_id FROM old_apart 
        WHERE manual_load_id = (SELECT manual_load_param FROM params)
    )
),
update_old_aparts AS (
    DELETE FROM old_apart  
    WHERE manual_load_id = (SELECT manual_load_param FROM params)
),
update_new_aparts AS (
    DELETE FROM new_apart 
    WHERE manual_load_id = (SELECT manual_load_param FROM params)
),
update_manual_load AS (
    DELETE FROM manual_load
    WHERE manual_load_id = (SELECT manual_load_param FROM params)
)
SELECT 'done' AS status;  