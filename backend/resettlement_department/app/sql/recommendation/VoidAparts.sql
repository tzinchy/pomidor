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
    SELECT affair_id, history_id, room_count, is_queue 
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
        na.room_count AS room_count,  -- 💡 вот тут!
        na.type_of_settlement, 
        na.notes, 
        na.new_apart_id,
        na.history_id,
        o.status_id,
        ai.room_count AS required_room_count,   -- 💡 и тут!
        ai.is_queue
    FROM new_apart na
    CROSS JOIN apart_info ai
    LEFT JOIN clr_dt o ON o.new_apart_id = na.new_apart_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM clr_dt dt
        WHERE dt.new_apart_id = na.new_apart_id AND dt.affair_id = ai.affair_id
    )
)
SELECT DISTINCT 
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
        notes, 
        new_apart_id,
        history_id,
        required_room_count,
        is_queue
FROM ranked_apartments
WHERE 
    CASE 
        WHEN is_queue = 1 THEN TRUE
        ELSE room_count = required_room_count
    END
    AND (ranked_apartments.status_id IS NULL OR ranked_apartments.status_id NOT IN (1,4,5,6,7))