WITH house_and_room_count AS (
	SELECT 
        house_address, 
        room_count, 
        COUNT(*) AS count
    FROM new_apart 
    WHERE status_id = 11
    GROUP BY house_address, room_count
    ORDER BY room_count
)
SELECT 
    house_address, 
    jsonb_object_agg(room_count, count) AS rooms
FROM house_and_room_count
GROUP BY house_address
ORDER BY house_address;