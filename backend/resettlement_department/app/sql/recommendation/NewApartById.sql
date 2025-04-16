WITH unnested_offer AS (
    SELECT 
        offer_id,
        affair_id,
        (KEY)::integer as new_apart_id,
        (VALUE->'status_id')::integer AS status_id,
        sentence_date, 
        answer_date,
        created_at,
        updated_at,
        (value->>'decline_reason_id')::integer AS decline_reason_id
    FROM offer, 
    jsonb_each(new_aparts)
    order by created_at ASC, updated_at ASC
),
joined_aparts AS (
    SELECT 
        o.offer_id,
        o.new_apart_id,
        JSONB_OBJECT_AGG( 
            o.affair_id::text,
            JSONB_BUILD_OBJECT( 
                'house_address', oa.house_address,
                'apart_number', oa.apart_number,
                'district', oa.district,
                'municipal_district', oa.municipal_district,
                'full_living_area', oa.full_living_area,
                'total_living_area', oa.total_living_area,
                'living_area', oa.living_area,
                'room_count', oa.room_count,
                'type_of_settlement', oa.type_of_settlement,
                'notes', oa.notes,
                'status', s.status,
                'sentence_date', o.sentence_date::DATE,
                'answer_date', o.answer_date::DATE,
                'decline_reason_id', o.decline_reason_id
            )
        ) AS offers
    FROM 
        unnested_offer o
    LEFT JOIN 
        new_apart na ON o.new_apart_id = na.new_apart_id
    LEFT JOIN 
        status s ON o.status_id = s.status_id
    LEFT JOIN
        decline_reason dr ON o.decline_reason_id = dr.decline_reason_id  
	LEFT JOIN old_apart  oa USING (affair_id)
    WHERE 
        o.new_apart_id IS NOT NULL  
    GROUP BY 
        o.offer_id,
        o.new_apart_id
)
SELECT
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
    JSONB_OBJECT_AGG(
        joined_aparts.offer_id::text,
        joined_aparts.offers
        ORDER BY joined_aparts.offer_id
    ) FILTER (WHERE joined_aparts.offer_id IS NOT NULL) AS offers
FROM new_apart  
LEFT JOIN joined_aparts USING (new_apart_id)
WHERE new_apart_id = :apart_id
GROUP BY
    new_apart.new_apart_id, 
    new_apart.house_address,
    new_apart.apart_number,
    new_apart.district,
    new_apart.municipal_district,
    new_apart.full_living_area,
    new_apart.total_living_area,
    new_apart.living_area,
    new_apart.room_count,
    new_apart.type_of_settlement
