WITH hstr_id AS (
    SELECT (%s)::int AS hs_id  
),
last_offers AS (
    SELECT affair_id, MAX(offer_id) AS last_offer_id
    FROM offer
    WHERE affair_id IN (
        SELECT affair_id 
        FROM old_apart 
        WHERE history_id = (SELECT hs_id FROM hstr_id)
    )
    GROUP BY affair_id
),
updated_offers AS (
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
    WHERE offer_id IN (SELECT last_offer_id FROM last_offers)
    RETURNING offer_id
)
SELECT 
    'done' AS result,
    COUNT(*) AS affected_rows
FROM updated_offers;