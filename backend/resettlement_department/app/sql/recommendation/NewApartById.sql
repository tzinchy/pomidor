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
                            'answer_date', o.answer_date :: DATE
                        ) ORDER BY sentence_date DESC, answer_date DESC
                        ) AS old_apartments
                                FROM 
                                    unnset_offer o
                                LEFT JOIN 
                                    old_apart ON old_apart.affair_id = o.affair_id
                                LEFT JOIN 
                                    status s ON o.status_id = s.status_id
                                GROUP BY 
                                    o.new_apart_id
                )
            SELECT new_apart.new_apart_id, 
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
                    from new_apart  
                    left join 
                    joined_aparts using (new_apart_id) 
					where new_apart_id = {apartment_id}