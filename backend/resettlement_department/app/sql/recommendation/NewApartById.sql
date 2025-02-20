WITH unnset_offer AS (
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
lft AS (
    SELECT 
        o.affair_id,
        o.new_apart_id,
        na.house_address,
        na.apart_number,
        na.district,
        na.municipal_district,
        na.full_living_area,
        na.total_living_area,
        na.living_area,
        na.room_count,
        na.type_of_settlement,
        na.notes,
        s.status,
        o.sentence_date,
        o.answer_date
    FROM 
        unnset_offer o 
        LEFT JOIN new_apart na USING (new_apart_id)
        LEFT JOIN status s ON o.status_id = s.status_id
),
old_apart_data AS (
    SELECT 
        oa.affair_id,
        oa.house_address,
        oa.apart_number,
        oa.district,
        oa.municipal_district,
        oa.full_living_area,
        oa.total_living_area,
        oa.living_area,
        oa.room_count,
        oa.type_of_settlement,
        o.sentence_date,
        o.answer_date
    FROM 
        old_apart oa
        LEFT JOIN unnset_offer o ON oa.affair_id = o.affair_id
)
SELECT 
	                na.new_apart_id,
                            na.house_address,
                            na.apart_number,
                            na.district,
                            na.municipal_district,
                            na.full_living_area,
                            na.total_living_area,
                            na.living_area,
                            na.room_count,
    jsonb_build_object(
        'old_apartments', 
        jsonb_agg(
            jsonb_build_object(
                'house_address', oa.house_address,
                'apart_number', oa.apart_number,
                'district', oa.district,
                'municipal_district', oa.municipal_district,
                'full_living_area', oa.full_living_area,
                'total_living_area', oa.total_living_area,
                'living_area', oa.living_area,
                'room_count', oa.room_count,
                'type_of_settlement', oa.type_of_settlement,
                'sentence_date', oa.sentence_date,
                'answer_date', oa.answer_date
            ) ORDER BY 
                oa.sentence_date DESC NULLS LAST, 
                oa.answer_date DESC NULLS LAST
        )
    ) AS result
FROM 
    lft na
    LEFT JOIN old_apart_data oa ON na.affair_id = oa.affair_id
    WHERE new_apart_id = {:new_apart_id}
GROUP BY 
    	                na.new_apart_id,
                            na.house_address,
                            na.apart_number,
                            na.district,
                            na.municipal_district,
                            na.full_living_area,
                            na.total_living_area,
                            na.living_area,
                            na.room_count
ORDER BY 
    na.new_apart_id;