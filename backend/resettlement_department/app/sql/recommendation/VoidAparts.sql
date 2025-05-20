WITH offered_aparts AS (
    SELECT 
        (KEY)::bigint AS new_apart_id
    FROM 
        offer, 
        jsonb_each(new_aparts)
	WHERE affair_id = :apart_id
),
apart_info AS (
    SELECT affair_id, history_id, room_count, is_queue, category, status_id, living_area, full_living_area, total_living_area
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
        ai.status_id AS old_apart_status_id,
        ai.room_count AS required_room_count,   -- 💡 и тут!
        ai.is_queue,
        ai.category,
        ai.living_area AS required_living_area,
        ai.full_living_area AS required_full_living_area,
        ai.total_living_area AS required_total_living_area
    FROM new_apart na
    CROSS JOIN apart_info ai
    WHERE na.status_id = 11
    AND new_apart_id NOT IN (SELECT * FROM offered_aparts)
)
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
    notes, 
    new_apart_id,
    history_id,
    required_room_count,
    is_queue
FROM ranked_apartments
WHERE
	CASE
		WHEN is_queue = 1 THEN TRUE
		WHEN category = 70 AND is_queue = 0 THEN living_area >= required_living_area
            AND full_living_area >= required_full_living_area
            AND total_living_area >= required_total_living_area
        ELSE TRUE
	END;