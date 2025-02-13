WITH hstr_id AS (
    SELECT (:history_id)::int AS hs_id  
),
updt_history AS (
    UPDATE history
    SET status_id = 1
    WHERE history_id = (SELECT hs_id FROM hstr_id)
),
updt_old_apart AS (
    UPDATE old_apart
    SET status_id = 6
    WHERE history_id = (SELECT hs_id FROM hstr_id)
),
updt_new_apart AS (
    UPDATE new_apart
    SET status_id = 6
    WHERE new_apart_id IN (
        SELECT key::int AS new_apart_id  
        FROM offer, jsonb_each(new_aparts)
)),
updt_offer AS (
    UPDATE offer
    SET
        status_id = 6,
        new_aparts = (
            SELECT COALESCE(
                jsonb_object_agg(
                    key,
                    jsonb_set(value, '{status_id}', '6'::jsonb)
                ),
                '{}'::jsonb
            )
            FROM jsonb_each(COALESCE(offer.new_aparts, '{}'::jsonb))
        )
    WHERE
        affair_id IN (
            SELECT affair_id
            FROM old_apart
            WHERE history_id = (SELECT hs_id FROM hstr_id)
        )
)
SELECT 1;