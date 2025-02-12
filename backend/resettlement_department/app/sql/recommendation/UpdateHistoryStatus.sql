WITH hstr_id AS (
    SELECT (:history_id)::int AS hs_id
),
updt AS (
    UPDATE history
    SET status_id = 7 
    WHERE history_id = (SELECT hs_id FROM hstr_id)
),
updt_offer AS ( 
    UPDATE offer 
    SET 
        status_id = 6,
        new_aparts = (
            SELECT 
                COALESCE(
                    jsonb_object_agg(
                        key, 
                        jsonb_set( 
                            value, 
                            '{status}', 
                            to_jsonb(6)
                        )
                    ),
                    '{}'::jsonb 
                )
            FROM 
                jsonb_each(COALESCE(new_aparts, '{}'::jsonb)) 
    WHERE 
        affair_id IN (
            SELECT affair_id 
            FROM family_apartment_needs 
            WHERE history_id = (SELECT hs_id FROM hstr_id)
        )
)
SELECT 1;