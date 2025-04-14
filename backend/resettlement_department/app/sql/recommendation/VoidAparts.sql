WITH apart_info AS (
    SELECT room_count, is_queue, is_special_needs_marker
    FROM old_apart 
    WHERE affair_id = :apart_id
),
offer_aparts AS (
    SELECT 
        (KEY)::int AS new_apart_id, 
        (VALUE->'status_id')::int AS status_id
    FROM offer, jsonb_each(new_aparts)
),
filtered_aparts AS (
    SELECT new_apart_id
    FROM new_apart
    WHERE new_apart_id IN (
        SELECT new_apart_id FROM offer_aparts WHERE status_id = 2
        UNION
        SELECT new_apart_id FROM new_apart
        EXCEPT
        SELECT new_apart_id FROM offer_aparts WHERE status_id <> 2
    )
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
        s.status,
        o.status_id, 
        na.for_special_needs_marker,
        ROW_NUMBER() OVER (
            PARTITION BY na.new_apart_id 
            ORDER BY o.sentence_date DESC, o.answer_date DESC, na.created_at DESC
        ) AS rn
    FROM 
        new_apart na
    JOIN 
        filtered_aparts fa ON fa.new_apart_id = na.new_apart_id
    LEFT JOIN (
        SELECT 
            (KEY)::int AS new_apart_id, 
            sentence_date, 
            answer_date, 
            (VALUE->'status_id')::int AS status_id 
        FROM 
            offer, 
            jsonb_each(new_aparts)
    ) o ON o.new_apart_id = na.new_apart_id
    LEFT JOIN 
        status s ON o.status_id = s.status_id
    WHERE 
        (o.status_id IS NULL OR o.status_id = 2)
        AND na.for_special_needs_marker = (SELECT is_special_needs_marker FROM apart_info)
        AND (
            (SELECT is_queue FROM apart_info) = 1 
            OR na.room_count = (SELECT room_count FROM apart_info)
        )
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
    status,
    status_id, 
    for_special_needs_marker
FROM 
    ranked_apartments
WHERE 
    rn = 1
ORDER BY 
    status;