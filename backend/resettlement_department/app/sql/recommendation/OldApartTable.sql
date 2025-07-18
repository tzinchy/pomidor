WITH ranked_apartments AS (
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
        was_queue,
		CASE
			WHEN (b.terms->'actual'->>'demolitionEnd')::date IS NOT NULL THEN 'Завершено'
			WHEN (b.terms->'actual'->>'secontResetlementEnd')::date IS NOT NULL THEN 'Снос'
			WHEN (b.terms->'actual'->>'firstResetlementEnd')::date IS NOT NULL THEN 'Отселение'
			WHEN (b.terms->'actual'->>'firstResetlementStart')::date IS NULL THEN 'Не начато'
			ELSE 'Переселение'
		END as "buildingRelocationStatus"
    FROM
        old_apart oa
    LEFT JOIN
        offer o USING (affair_id)
    LEFT JOIN
        status ON oa.status_id = status.status_id
	LEFT JOIN renovation.apartments_old_temp using (affair_id)
	LEFT join renovation.buildings_old b on apartments_old_temp.building_id = b.id 
    WHERE is_hidden = False
)
SELECT *
FROM ranked_apartments