WITH unnset_offer AS (
                SELECT 
                    affair_id,
                    (KEY)::integer as new_apart_id,
                    (VALUE->'status_id')::integer AS status_id,
                    sentence_date, 
                    answer_date
                    FROM offer, 
                    jsonb_each(new_aparts)
            ),
                joined_aparts AS (
                    SELECT 
                    affair_id,
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
                            'status', s.status,
                            'sentence_date', o.sentence_date :: DATE,
                            'answer_date', o.answer_date :: DATE
                        ) ORDER BY sentence_date DESC, answer_date DESC
                        ) AS new_apartments
                                FROM 
                                    unnset_offer o
                                LEFT JOIN 
                                    new_apart na ON o.new_apart_id = na.new_apart_id
                                LEFT JOIN 
                                    status s ON o.status_id = s.status_id
                                GROUP BY 
                                    o.affair_id
                )
            SELECT old_apart.affair_id, 
                    old_apart.house_address,
                    old_apart.apart_number,
                    old_apart.district,
                    old_apart.municipal_district,
                    old_apart.full_living_area,
                    old_apart.total_living_area,
                    old_apart.living_area,
                    old_apart.room_count,
                    old_apart.type_of_settlement,
                    joined_aparts.new_apartments
                    from old_apart  
                    left join 
                    joined_aparts using (affair_id) 
                    WHERE affair_id = {apartment_id}       