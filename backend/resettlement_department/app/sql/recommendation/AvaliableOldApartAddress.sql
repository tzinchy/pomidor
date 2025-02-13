WITH needs_with_row AS (
    SELECT 
        family_apartment_needs_id,
        status_id,
        ROW_NUMBER() OVER (
            PARTITION BY family_apartment_needs.family_apartment_needs_id 
            ORDER BY offer.sentence_date DESC, offer.answer_date DESC
        ) AS rn
    FROM family_apartment_needs
    JOIN offer USING (family_apartment_needs_id)
),
clear_data AS (
    SELECT family_apartment_needs_id 
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
    FROM family_apartment_needs 
    JOIN family_structure USING (affair_id)
    WHERE NOT EXISTS (
        SELECT 1
        FROM clear_data
        WHERE clear_data.family_apartment_needs_id = family_apartment_needs.family_apartment_needs_id
    )
    GROUP BY house_address, room_count
    ORDER BY room_count
) AS subquery
GROUP BY house_address
ORDER BY house_address;