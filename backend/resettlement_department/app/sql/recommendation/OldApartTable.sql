WITH ranked_apartments AS (
    SELECT
        offer_id,
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
        is_queue,
        ROW_NUMBER() OVER (PARTITION BY oa.affair_id ORDER BY o.sentence_date DESC, o.answer_date DESC, o.created_at DESC) AS rn,
        COUNT(o.affair_id) OVER (PARTITION BY oa.affair_id) AS selection_count
    FROM
        old_apart oa
    LEFT JOIN
        offer o USING (affair_id)
    LEFT JOIN
        status ON o.status_id = status.status_id
)
SELECT *
FROM ranked_apartments
