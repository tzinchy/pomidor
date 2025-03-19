WITH updated_data AS (
    SELECT
        offer_id,
        new_apart_id,
        jsonb_set(
            new_aparts->(new_apart_id),
            '{status_id}',
            to_jsonb((SELECT status_id FROM status WHERE status = :status))
        ) AS updated_value
    FROM
        offer,
        jsonb_each(new_aparts) AS each(new_apart_id, value)
    WHERE
        offer_id = (SELECT MAX(offer_id) FROM offer where affair_id = (:apart_id)) and new_apart_id = :new_apart_id and affair_id = :apart_id
)
UPDATE offer
SET new_aparts = jsonb_set(
    new_aparts,
    ARRAY[updated_data.new_apart_id],
    updated_data.updated_value
)
FROM updated_data
WHERE offer.offer_id = updated_data.offer_id;