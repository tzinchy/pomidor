WITH hstr_id AS (
    SELECT (:history_id)::int AS hs_id  
),
updt_history AS (
    UPDATE history
    SET status_id = 1
    WHERE history_id = (SELECT hs_id FROM hstr_id)
),
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