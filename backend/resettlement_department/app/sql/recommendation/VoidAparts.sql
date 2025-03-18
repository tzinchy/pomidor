WITH clr_dt AS (
    SELECT 
        affair_id, 
        (KEY)::int AS new_apart_id, 
        sentence_date, 
        answer_date, 
        (VALUE->'status_id')::int AS status_id 
    FROM 
        offer, 
        jsonb_each(new_aparts)
),
apart_info AS (
    SELECT history_id, room_count, is_queue 
    FROM old_apart 
    WHERE affair_id = :apart_id
),
ranked_apartments AS (
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
        na.history_id, 
        s.status AS status,
        o.status_id, 
        ROW_NUMBER() OVER (
            PARTITION BY na.new_apart_id 
            ORDER BY o.sentence_date DESC, o.answer_date DESC, na.created_at ASC
        ) AS rn
    FROM 
        new_apart na
    LEFT JOIN 
        clr_dt as o on o.new_apart_id = na.new_apart_id
    LEFT JOIN 
        status s ON o.status_id = s.status_id
    WHERE na.new_apart_id NOT IN (SELECT new_apart_id FROM clr_dt)
)
SELECT *
FROM ranked_apartments
WHERE 
    CASE 
        WHEN (SELECT is_queue FROM apart_info) = 1 THEN TRUE
        ELSE ranked_apartments.room_count = (SELECT room_count FROM apart_info)
    END
    AND (status_id IS NULL OR status_id NOT IN (1,4,5,6,7))
ORDER BY status;