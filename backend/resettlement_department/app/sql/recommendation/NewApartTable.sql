WITH ranked_apartments AS (
    SELECT 
        house_address, 
        apart_number, 
        district, 
        municipal_district,
        floor,
        full_living_area,
        total_living_area, 
        living_area, 
        room_count, 
        type_of_settlement, 
        status.status AS status, 
        new_apart.notes, 
        new_apart.new_apart_id,
        ROW_NUMBER() OVER (PARTITION BY new_apart.new_apart_id ORDER BY offer.sentence_date DESC, offer.answer_date DESC) AS rn
    FROM 
        new_apart
    LEFT JOIN 
        offer USING (new_apart_id)
    LEFT JOIN 
        status ON offer.status_id = status.status_id
)
SELECT *
FROM ranked_apartments
WHERE {where_clause}
ORDER BY full_living_area
