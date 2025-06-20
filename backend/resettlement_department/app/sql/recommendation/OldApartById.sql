WITH unnested_offer AS (
    SELECT 
        offer_id,
        affair_id,
        (key)::bigint AS new_apart_id,
        (value->'status_id')::integer AS status_id,
        sentence_date, 
        answer_date, 
        created_at, 
        updated_at,
        (value->>'decline_reason_id')::integer AS decline_reason_id 
    FROM offer, 
    jsonb_each(new_aparts) AS each(key, value)
),
joined_aparts AS (
    SELECT 
        o.offer_id,
        o.affair_id,
        JSONB_OBJECT_AGG( 
            o.new_apart_id::text,
            JSONB_BUILD_OBJECT( 
                'house_address', na.house_address,
                'apart_number', na.apart_number,
                'district', na.district,
                'municipal_district', na.municipal_district,
                'full_living_area', na.full_living_area,
                'total_living_area', na.total_living_area,
                'living_area', na.living_area,
                'room_count', na.room_count,
                'type_of_settlement', na.type_of_settlement,
                'notes', na.notes,
                'status', s.status,
                'sentence_date', o.sentence_date::DATE,
                'answer_date', o.answer_date::DATE,
                'decline_reason_id', o.decline_reason_id,
                'created_at', o.created_at::DATE,
                'floor', na.floor,
                'decline_reason', JSONB_BUILD_OBJECT(
                    'min_floor', dr.min_floor, 
                    'max_floor', dr.max_floor, 
                    'unom', dr.unom, 
                    'entrance', dr.entrance, 
                    'apartment_layout', dr.apartment_layout, 
                    'notes', dr.notes
                )
            )
        ) AS new_apartments
    FROM 
        unnested_offer o
    LEFT JOIN 
        new_apart na ON o.new_apart_id = na.new_apart_id
    LEFT JOIN 
        status s ON o.status_id = s.status_id
    LEFT JOIN 
        decline_reason dr ON o.decline_reason_id = dr.decline_reason_id  
    WHERE 
        o.new_apart_id IS NOT NULL  
    GROUP BY 
        o.offer_id,
        o.affair_id
)
SELECT 
    old_apart.affair_id, 
    old_apart.house_address,
    old_apart.apart_number,
    old_apart.district,
    old_apart.municipal_district,
    old_apart.fio,
    old_apart.full_living_area,
    old_apart.total_living_area,
    old_apart.living_area,
    old_apart.room_count,
    old_apart.type_of_settlement,
    old_apart.is_queue,
    old_apart.people_v_dele,
    old_apart.rank,
    old_apart.floor,
	affair_timeline.timeline_events,
    old_apart.status_id,
    JSONB_OBJECT_AGG(
        joined_aparts.offer_id::text,
        joined_aparts.new_apartments
        ORDER BY joined_aparts.offer_id
    ) FILTER (WHERE joined_aparts.offer_id IS NOT NULL) AS offers
FROM
    old_apart  
LEFT JOIN 
    joined_aparts ON old_apart.affair_id = joined_aparts.affair_id
LEFT JOIN affair_timeline ON affair_timeline.old_apart_id = old_apart.affair_id
WHERE old_apart.affair_id = :apart_id
GROUP BY 
    old_apart.affair_id, 
    old_apart.house_address,
    old_apart.apart_number,
    old_apart.district,
    old_apart.municipal_district,
    old_apart.fio,
    old_apart.full_living_area,
    old_apart.total_living_area,
    old_apart.living_area,
    old_apart.room_count,
    old_apart.type_of_settlement,
    old_apart.is_queue,
    old_apart.people_v_dele,
    old_apart.rank,
	affair_timeline.timeline_events,
    old_apart.status_id;