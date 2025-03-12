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
    select history_id, room_count from old_apart where affair_id = :apart_id
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
)
SELECT *
FROM ranked_apartments
WHERE ranked_apartments.history_id = (select history_id from apart_info) and ranked_apartments.room_count = (select room_count from apart_info)
and (status_id is null or status_id != 7)
ORDER BY status;