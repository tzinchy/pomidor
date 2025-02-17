WITH new_apartment_list AS (
    SELECT 
        o.family_apartment_needs_id,
        JSON_AGG(
            JSON_BUILD_OBJECT(
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
                'status', COALESCE(s.status, '?'),
                'sentence_date', o.sentence_date :: DATE,
                'answer_date', o.answer_date :: DATE
            )
        ) FILTER (WHERE na.house_address IS NOT NULL OR na.apart_number IS NOT NULL OR na.district IS NOT NULL OR na.municipal_district IS NOT NULL 
        OR na.full_living_area IS NOT NULL OR na.total_living_area IS NOT NULL OR na.living_area IS NOT NULL 
        OR na.room_count IS NOT NULL OR na.type_of_settlement IS NOT NULL OR na.notes IS NOT NULL 
        OR s.status IS NOT NULL OR o.sentence_date IS NOT NULL OR o.answer_date IS NOT NULL) AS new_apartments
    FROM 
        offer o
    LEFT JOIN 
        new_apart na ON o.new_apart_id = na.new_apart_id
    LEFT JOIN 
        status s ON o.status_id = s.status_id
    GROUP BY 
        o.family_apartment_needs_id
)
SELECT 
    fan.family_apartment_needs_id,
    fs.house_address,
    fs.apart_number,
    fs.district,
    fs.municipal_district,
    fs.full_living_area,
    fs.total_living_area,
    fs.living_area,
    fs.room_count,
    fs.type_of_settlement,
    nal.new_apartments
FROM 
    family_apartment_needs fan
LEFT JOIN 
    family_structure fs ON fan.affair_id = fs.affair_id
LEFT JOIN 
    new_apartment_list nal ON fan.family_apartment_needs_id = nal.family_apartment_needs_id
WHERE
    fan.family_apartment_needs_id = {apartment_id}
ORDER BY 
    fs.affair_id;
