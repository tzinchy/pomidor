WITH ranked_apartments AS (
    SELECT
        house_address,
        apart_number,
        district,
        municipal_district,
        floor,
        fio,
        full_living_area,
        total_living_area,
        living_area,
        room_count,
        type_of_settlement,
        status.status,
        o.notes,
        affair_id,
        ROW_NUMBER() OVER (PARTITION BY oa.affair_id ORDER BY o.sentence_date DESC, o.answer_date DESC) AS rn
    FROM
        old_apart oa
    LEFT JOIN
        offer o USING (affair_id)
    LEFT JOIN
        status ON o.status_id = status.status_id
)
SELECT *
FROM ranked_apartments
WHERE 1=1 and {where_clause}
ORDER BY full_living_area