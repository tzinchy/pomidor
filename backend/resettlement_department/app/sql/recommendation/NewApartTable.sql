WITH ranked_apartments AS (
    SELECT 
        na.house_address, 
        na.apart_number, 
        na.district, 
        na.municipal_district,
        na.floor,
        na.full_living_area,
        na.total_living_area, 
        na.living_area, 
        na.room_count, 
        na.type_of_settlement, 
        na.notes, 
        na.new_apart_id,
        s.status AS status,
        ROW_NUMBER() OVER (
            PARTITION BY na.new_apart_id 
            ORDER BY o.sentence_date DESC NULLS LAST, o.answer_date DESC NULLS LAST
        ) AS rn
    FROM 
        new_apart na
    LEFT JOIN 
        offer o ON na.new_apart_id = (o.new_aparts::jsonb ->> 'new_apart_id')::int
    LEFT JOIN 
        status s ON o.status_id = s.status_id
)
SELECT *
FROM ranked_apartments
WHERE 1=1 and rn = 1 and {where_clause}
ORDER BY full_living_area;
