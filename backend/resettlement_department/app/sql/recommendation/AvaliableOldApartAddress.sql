WITH needs_with_row AS (
    SELECT 
        affair_id,
        offer.status_id,
        ROW_NUMBER() OVER (
            PARTITION BY old_apart.affair_id 
            ORDER BY offer.sentence_date DESC, offer.answer_date DESC
        ) AS rn
    FROM old_apart
    JOIN offer USING (affair_id)
),
clear_data AS (
    SELECT affair_id 
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
        COUNT(room_count) AS count
    FROM old_apart 
    WHERE NOT EXISTS (
        SELECT 1
        FROM clear_data
        WHERE clear_data.affair_id = old_apart.affair_id
    ) and (rsm_status <> 'снято' or rsm_status is Null)
    GROUP BY house_address, room_count
    ORDER BY room_count
) AS subquery
GROUP BY house_address
ORDER BY house_address;