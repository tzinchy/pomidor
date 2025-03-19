WITH unnset_offer AS (
    SELECT 
        offer_id,
        affair_id,
        (KEY)::integer as new_apart_id,
        (VALUE->'status_id')::integer AS status_id,
        sentence_date, 
        answer_date,
        created_at,
        updated_at,
        declined_reason_id
    FROM offer, 
    jsonb_each(new_aparts)
    order by created_at ASC, updated_at ASC
),
joined_aparts AS (
    SELECT 
        o.offer_id,
        o.new_apart_id,
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'house_address', old_apart.house_address,
                'apart_number', old_apart.apart_number,
                'district', old_apart.district,
                'municipal_district', old_apart.municipal_district,
                'full_living_area', old_apart.full_living_area,
                'total_living_area', old_apart.total_living_area,
                'living_area', old_apart.living_area,
                'room_count', old_apart.room_count,
                'type_of_settlement', old_apart.type_of_settlement,
                'notes', old_apart.notes,
                'status', s.status,
                'sentence_date', o.sentence_date :: DATE,
                'answer_date', o.answer_date :: DATE,
                'decline_reason_notes', dr.notes
            ) ORDER BY sentence_date DESC, answer_date DESC, o.created_at ASC, o.updated_at ASC
        ) AS old_apartments
    FROM 
        unnset_offer o
    LEFT JOIN 
        old_apart ON old_apart.affair_id = o.affair_id
    LEFT JOIN 
        status s ON o.status_id = s.status_id
    LEFT JOIN 
        decline_reason AS dr USING (declined_reason_id)
    GROUP BY 
        o.offer_id,
        o.new_apart_id
)
SELECT 
    joined_aparts.offer_id
    new_apart.new_apart_id, 
    new_apart.house_address,
    new_apart.apart_number,
    new_apart.district,
    new_apart.municipal_district,
    new_apart.full_living_area,
    new_apart.total_living_area,
    new_apart.living_area,
    new_apart.room_count,
    new_apart.type_of_settlement,
    joined_aparts.old_apartments
FROM new_apart  
LEFT JOIN joined_aparts USING (new_apart_id) 
WHERE new_apart_id = :apart_id