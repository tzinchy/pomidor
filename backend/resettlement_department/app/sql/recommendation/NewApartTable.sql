WITH clr_dt AS (
    SELECT 
        offer_id,
        affair_id, 
        (KEY)::int AS new_apart_id, 
        sentence_date, 
        answer_date, 
		created_at,
		updated_at,
        (VALUE->'status_id')::int AS status_id 
    FROM 
        offer, 
        jsonb_each(new_aparts)
),
ranked_apartments AS (
    SELECT 
        o.offer_id,
        o.created_at::DATE,
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
        na.entrance_number,
        CASE WHEN na.notes IS NULL THEN na.rsm_notes ELSE na.rsm_notes || ';' || na.notes END AS notes,
        na.new_apart_id,
        s.status AS status,
        is_private,
        for_special_needs_marker,
        ROW_NUMBER() OVER (
            PARTITION BY na.new_apart_id 
            ORDER BY o.sentence_date DESC, o.answer_date DESC, o.created_at DESC
        ) AS rn,
        COUNT(o.affair_id) OVER (PARTITION BY na.new_apart_id) AS selection_count, 
        rank
    FROM 
        new_apart na
    LEFT JOIN 
        clr_dt as o on o.new_apart_id = na.new_apart_id
    LEFT JOIN 
        status s ON na.status_id = s.status_id
)
SELECT *
FROM ranked_apartments
