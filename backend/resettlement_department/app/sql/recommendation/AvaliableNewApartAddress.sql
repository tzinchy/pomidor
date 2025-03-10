WITH unnst AS (
	SELECT 
	(key)::integer as new_apart_id, 
	(value->'status_id')::integer as status_id,
	sentence_date, 
	answer_date
	FROM offer, jsonb_each(new_aparts)
),
needs_with_row AS (
    SELECT 
        new_apart_id,
        status_id,
        ROW_NUMBER() OVER (
            PARTITION BY new_apart_id 
            ORDER BY offer.sentence_date DESC, offer.answer_date DESC
        ) AS rn
    FROM unnst as offer
),
clear_data AS (
    SELECT new_apart_id 
    FROM needs_with_row 
    WHERE rn = 1 AND status_id != 2
)
SELECT 
    house_address, 
    jsonb_object_agg(room_count, count) AS rooms
FROM (
    SELECT 
        house_address, 
        room_count, 
        COUNT(*) AS count
    FROM new_apart 
    WHERE NOT EXISTS (
        SELECT 1 
        FROM clear_data 
        WHERE clear_data.new_apart_id = new_apart.new_apart_id
    )
    GROUP BY house_address, room_count
    ORDER BY room_count
) AS subquery
GROUP BY house_address
ORDER BY house_address;