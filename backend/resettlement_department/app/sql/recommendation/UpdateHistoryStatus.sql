WITH hstr_id AS (
    SELECT (:history_id) ::int AS hs_id
),
updt AS (
    UPDATE history
    SET status_id = 7 
    WHERE history_id = (SELECT hs_id FROM hstr_id)
),
updt_offer AS ( 
    UPDATE offer 
    SET status_id = 6
    WHERE family_apartment_needs_id IN (
        SELECT family_apartment_needs_id 
        FROM offer  
        WHERE family_apartment_needs_id in (SELECT family_apartment_needs_id FROM family_apartment_needs WHERE history_id = (SELECT hs_id FROM hstr_id))
    )
)
SELECT 1;  
