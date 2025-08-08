WITH ranked_apartments AS (
    -- Your existing CTE
    SELECT
        offer_id,
        o.created_at::DATE,
        oa.house_address,
        oa.apart_number,
        oa.district,
        oa.municipal_district,
        oa.floor,
        oa.fio,
        oa.full_living_area,
        oa.total_living_area,
        oa.living_area,
        oa.room_count,
        oa.type_of_settlement,
        status.status as status,
        CASE WHEN oa.notes IS NULL THEN oa.rsm_notes ELSE oa.rsm_notes || ';' || oa.notes END AS notes,
        oa.affair_id,
        oa.is_queue,
        oa.is_special_needs_marker,
        ROW_NUMBER() OVER (PARTITION BY oa.affair_id ORDER BY o.sentence_date DESC, o.answer_date DESC, o.created_at DESC) AS rn,
        COUNT(o.affair_id) OVER (PARTITION BY oa.affair_id) AS selection_count,
        oa.people_v_dele,
        oa.rank,
        apartments_old_temp.classificator,
        apartments_old_temp.dates,
        was_queue
    FROM
        old_apart oa
    LEFT JOIN
        offer o USING (affair_id)
    LEFT JOIN
        status ON oa.status_id = status.status_id
    LEFT JOIN 
        renovation.apartments_old_temp USING (affair_id)
    WHERE 
        is_hidden = False AND classificator IS NOT NULL
),
job_is_done AS (
    SELECT ra.*
    FROM ranked_apartments AS ra
    WHERE classificator ->> 'action'::text = 'Работа завершена'
),
offer_unnst AS (
    SELECT offer_id, affair_id, KEY::bigint as new_apart_id, VALUE->>'outcoming_date' as outcoming_date, (value->>'status_id')::int as status_id
    FROM offer,
    jsonb_each(new_aparts)
),
matching AS (
    SELECT 
        offer_unnst.offer_id, 
        outcoming_date, 
        old_apart.affair_id, 
		old_apart.district,
		old_apart.municipal_district,
        old_apart.house_address as old_house_address, 
        old_apart.apart_number as old_apart_number, 
        old_apart.fio as fio, 
        new_apart.new_apart_id, 
        new_apart.house_address as new_apart_house_address, 
        new_apart.apart_number, 
        status.status,
        job_is_done.classificator,
        job_is_done.dates
    FROM offer_unnst
    LEFT JOIN old_apart ON old_apart.affair_id = offer_unnst.affair_id 
    LEFT JOIN new_apart ON new_apart.new_apart_id = offer_unnst.new_apart_id
    LEFT JOIN status ON status.status_id = offer_unnst.status_id
    JOIN job_is_done ON offer_unnst.affair_id = job_is_done.affair_id
),
cleared AS (
    SELECT DISTINCT * FROM matching
),
numbered_offers AS (
    SELECT 
        c.*,
        ROW_NUMBER() OVER (PARTITION BY c.affair_id ORDER BY c.outcoming_date) AS offer_number
    FROM 
        cleared c
)

-- Final analysis with all status categories
SELECT 
	old_house_address,
    offer_number as "С какого раза",
    COUNT(DISTINCT affair_id) FILTER (WHERE status IN ('Согласие', 'МФР Компенсация', 'МФР Докупка', 'МФР (вне района)')) AS "Согласие",
    COUNT(DISTINCT affair_id) FILTER (WHERE status = 'Суд') AS "Суд",
    COUNT(DISTINCT affair_id) FILTER (WHERE status = 'Отказ (Выход из Суда)') AS "Выход из суда",
    COUNT(DISTINCT affair_id) FILTER (WHERE status = 'Отказ') AS "Отказ",
    COUNT(DISTINCT affair_id) FILTER (WHERE status = 'Ожидание') AS "Ожидание",
    COUNT(DISTINCT affair_id) FILTER (WHERE status = 'Ждет одобрения') AS "Ждет одобрения",
    COUNT(DISTINCT affair_id) AS "Всего случаев"
FROM 
    numbered_offers
GROUP BY 
    old_house_address, offer_number
ORDER BY 
    old_house_address, offer_number;