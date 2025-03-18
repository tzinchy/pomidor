WITH apartment_totals AS (
    SELECT 
        building_id,
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE (classificator->>'deviation')::varchar = 'Работа завершена'::varchar) as done,
        COUNT(*) FILTER (WHERE (classificator->>'deviation')::varchar = 'В работе у МФР'::varchar) as mfr,
        COUNT(*) FILTER (WHERE (classificator->>'deviation')::varchar = 'Без отклонений'::varchar) as none,
        COUNT(*) FILTER (WHERE (classificator->>'deviation')::varchar = 'Риск'::varchar) as risk,
        COUNT(*) FILTER (WHERE (classificator->>'deviation')::varchar = 'Требует внимания'::varchar) as attention
    FROM renovation.apartments_old_temp
    GROUP BY building_id
), building_info AS (
    SELECT  
        b.id, 
        b.okrug, 
        b.okrug_order as "okrugOrder",
        b.status_order as "statusOrder",
        b.district, 
        b.adress, 
        COALESCE(b.manual_relocation_type, b.relocation_type) as "relocationTypeId",
        rt.type as relocationType,
        CASE
            WHEN (b.terms->>'doneDate')::date IS NOT NULL THEN 'Работа завершена'::text
            WHEN COALESCE(b.manual_relocation_type, b.relocation_type) = ANY(ARRAY[2,3]) OR b.moves_outside_district = true THEN 'Без отклонений'::text
            WHEN at.risk > 0 THEN 'Наступили риски'::text
            WHEN at.attention > 0 THEN 'Требует внимания'::text
            ELSE 'Без отклонений'::text
        END AS buildingDeviation,
        CASE
            WHEN (b.terms->'actual'->>'firstResetlementStart')::date IS NULL THEN 'Не начато'
            WHEN COALESCE((b.terms->>'doneDate')::date, NOW()) - (b.terms->'actual'->>'firstResetlementStart')::date < '1 month' THEN 'Менее месяца'
            WHEN COALESCE((b.terms->>'doneDate')::date, NOW()) - (b.terms->'actual'->>'firstResetlementStart')::date < '2 month' THEN 'От 1 до 2 месяцев'
            WHEN COALESCE((b.terms->>'doneDate')::date, NOW()) - (b.terms->'actual'->>'firstResetlementStart')::date < '5 month' THEN 'От 2 до 5 месяцев'
            WHEN COALESCE((b.terms->>'doneDate')::date, NOW()) - (b.terms->'actual'->>'firstResetlementStart')::date < '8 month' THEN 'От 5 до 8 месяцев'
            ELSE 'Более 8 месяцев'
        END as buildingRelocationStartAge,
        CASE
            WHEN (b.terms->'actual'->>'demolitionEnd')::date IS NOT NULL THEN 'Завершено'
            WHEN (b.terms->'actual'->>'secontResetlementEnd')::date IS NOT NULL THEN 'Снос'
            WHEN (b.terms->'actual'->>'firstResetlementEnd')::date IS NOT NULL THEN 'Отселение'
            WHEN (b.terms->'actual'->>'firstResetlementStart')::date IS NULL THEN 'Не начато'
            ELSE 'Переселение'
        END as buildingRelocationStatus,
        b.terms,
        jsonb_build_object('total', COALESCE(at.total, 0)::integer, 
                            'deviation', json_build_object(
                                'done', COALESCE(at.done, 0)::integer,
                                'mfr', COALESCE(at.mfr, 0)::integer,
                                'none', COALESCE(at.none, 0)::integer,
                                'attention', COALESCE(at.attention, 0)::integer,
                                'risk', COALESCE(at.risk, 0)::integer
                            )) as apartments
    FROM renovation.buildings_old b
    LEFT JOIN apartment_totals at ON at.building_id = b.id
    LEFT JOIN renovation.relocation_types rt ON rt.id = COALESCE(b.manual_relocation_type, b.relocation_type)
)
SELECT
    cbc.new_building_id, 
    bn.okrug, 
    bn.district, 
    bn.adress as New_adress,
    jsonb_object_agg(
        b.id,
        (b.adress, b.buildingDeviation, b.buildingRelocationStartAge, b.buildingRelocationStatus, b.terms,  b.apartments, b.relocationType)
    ) AS building_details,
    -- Добавляем столбец status_flag
    CASE 
        WHEN MAX(CASE WHEN b.terms->>'doneDate' IS NULL AND b.buildingDeviation = 'Наступили риски' THEN 1 ELSE 0 END) = 1 THEN 'Наступили риски'
        WHEN MAX(CASE WHEN b.terms->>'doneDate' IS NULL AND b.buildingDeviation = 'Требует внимания' THEN 1 ELSE 0 END) = 1 THEN 'Требует внимания'
        WHEN MAX(CASE WHEN b.terms->>'doneDate' IS NULL AND b.buildingDeviation = 'Без отклонений' THEN 1 ELSE 0 END) = 1 THEN 'Без отклонений'
        ELSE 'Работа завершена'
    END AS status_flag,
    -- Рассчитываем otsel_type
    CASE
        WHEN max(CASE WHEN (b.terms->>'doneDate') IS NULL THEN 0 ELSE 1 END) = 0
            AND max(CASE WHEN (b.terms->'actual'->>'firstResetlementStart') IS NOT NULL THEN 1 ELSE 0 END) = 0 THEN 'Освобождение не начато'
        WHEN MIN(CASE WHEN (b.terms->>'doneDate') IS NULL THEN 0 ELSE 1 END) = 0
            AND MIN(CASE WHEN (b.terms->'actual'->>'firstResetlementStart') IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN 'Идёт полное освобождение'
        WHEN MIN(CASE WHEN (b.terms->>'doneDate') IS NULL THEN 0 ELSE 1 END) = 0
            AND MAX(CASE WHEN (b.terms->'actual'->>'firstResetlementStart') IS NOT NULL THEN 1 ELSE 0 END) = 1 
            AND MIN(CASE WHEN (b.terms->'actual'->>'firstResetlementStart') IS NOT NULL THEN 1 ELSE 0 END) = 0 THEN 'Идёт частичное освобождение'
        ELSE 'Освобождены'
    END AS otsel_type,
    -- Новый столбец для минимального диапазона срока
    CASE
        WHEN MIN(CASE WHEN b.terms->>'doneDate' IS NULL THEN b.buildingRelocationStartAge ELSE NULL END) = 'Менее месяца' THEN 'Менее месяца'
        WHEN MIN(CASE WHEN b.terms->>'doneDate' IS NULL THEN b.buildingRelocationStartAge ELSE NULL END) = 'От 1 до 2 месяцев' THEN 'От 1 до 2 месяцев'
        WHEN MIN(CASE WHEN b.terms->>'doneDate' IS NULL THEN b.buildingRelocationStartAge ELSE NULL END) = 'От 2 до 5 месяцев' THEN 'От 2 до 5 месяцев'
        WHEN MIN(CASE WHEN b.terms->>'doneDate' IS NULL THEN b.buildingRelocationStartAge ELSE NULL END) = 'От 5 до 8 месяцев' THEN 'От 5 до 8 месяцев'
        WHEN MIN(CASE WHEN b.terms->>'doneDate' IS NULL THEN b.buildingRelocationStartAge ELSE NULL END) = 'Более 8 месяцев' THEN 'Более 8 месяцев'
        ELSE 'Не начато'
    END AS date_diapazon
FROM building_info b
JOIN renovation.connection_building_construction cbc ON b.id = cbc.old_building_id
JOIN renovation.buildings_new bn ON cbc.new_building_id = bn.id
GROUP BY cbc.new_building_id, bn.adress, bn.okrug, bn.district, bn.terms
ORDER BY otsel_type, status_flag, cbc.new_building_id