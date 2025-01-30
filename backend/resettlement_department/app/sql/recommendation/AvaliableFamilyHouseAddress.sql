SELECT 
    house_address, 
    jsonb_object_agg(room_count, count) AS rooms
FROM (
    SELECT 
        house_address, 
        room_count, 
        COUNT(room_count) AS count
    FROM family_apartment_needs 
    JOIN family_structure USING (affair_id)
    GROUP BY house_address, room_count
    ORDER BY room_count 
) AS subquery
GROUP BY house_address
ORDER BY house_address;

