WITH unnested_offer AS (
    SELECT 
        offer_id,
        affair_id,
        (KEY)::bigint as new_apart_id,
        (VALUE->'status_id')::integer AS status_id,
        sentence_date, 
        answer_date,
        created_at,
        updated_at,
        (value->>'decline_reason_id')::integer AS decline_reason_id
    FROM offer, 
        jsonb_each(new_aparts)
),
spd1_filtered AS (
    SELECT
        offer_id,
        appid,
        appname,
        appdate,
        pgudate,
        kpu_num,
        cad_num,
        docname,
        signstatus,
        createdate,
        signeddocname,
        signeddocdate
    FROM spd1
),
joined_aparts AS (
    SELECT 
        o.offer_id,
        o.new_apart_id,
        JSONB_OBJECT_AGG( 
            o.affair_id::text,
            JSONB_BUILD_OBJECT( 
                'house_address', oa.house_address,
                'apart_number', oa.apart_number,
                'district', oa.district,
                'municipal_district', oa.municipal_district,
                'full_living_area', oa.full_living_area,
                'total_living_area', oa.total_living_area,
                'living_area', oa.living_area,
                'room_count', oa.room_count,
                'type_of_settlement', oa.type_of_settlement,
                'notes', oa.notes,
                'status', s.status,
                'sentence_date', o.sentence_date::DATE,
                'answer_date', o.answer_date::DATE,
                'decline_reason_id', o.decline_reason_id,
                'created_at', o.created_at::DATE,

                --spd1
                'spd_appid', s1.appid,
                'spd_appname', s1.appname,
                'spd_appdate', s1.appdate,
                'spd_pgudate', s1.pgudate,
                'spd_kpu_num', s1.kpu_num,
                'spd_cad_num', s1.cad_num,
                'spd_docname', s1.docname,
                'spd_signstatus', s1.signstatus,
                'spd_createdate', s1.createdate,
                'spd_signeddocname', s1.signeddocname,
                'spd_signeddocdate', s1.signeddocdate
            )
        ) AS offers
    FROM 
        unnested_offer o
    LEFT JOIN 
        new_apart na ON o.new_apart_id = na.new_apart_id
    LEFT JOIN 
        status s ON o.status_id = s.status_id
    LEFT JOIN 
        decline_reason dr ON o.decline_reason_id = dr.decline_reason_id  
    LEFT JOIN 
        old_apart oa USING (affair_id)
    LEFT JOIN 
        spd1_filtered s1 ON o.offer_id = s1.offer_id
    WHERE 
        o.new_apart_id IS NOT NULL  
    GROUP BY 
        o.offer_id,
        o.new_apart_id
)

SELECT
    new_apart.new_apart_id, 
    new_apart.house_address,
    new_apart.apart_number,
    new_apart.district,
    new_apart.municipal_district,
    new_apart.full_living_area,
    new_apart.total_living_area,
    new_apart.living_area,
    new_apart.room_count,
    new_apart.type_of_settlement,
    new_apart.rank,
    new_apart.floor,
    new_apart.rsm_apart_id, 
    new_apart.status_id,

    JSONB_OBJECT_AGG(
        joined_aparts.offer_id::text,
        joined_aparts.offers
        ORDER BY joined_aparts.offer_id
    ) FILTER (WHERE joined_aparts.offer_id IS NOT NULL) AS offers

FROM new_apart  
LEFT JOIN joined_aparts USING (new_apart_id)
WHERE new_apart.new_apart_id = :apart_id
GROUP BY
    new_apart.new_apart_id, 
    new_apart.house_address,
    new_apart.apart_number,
    new_apart.district,
    new_apart.municipal_district,
    new_apart.full_living_area,
    new_apart.total_living_area,
    new_apart.living_area,
    new_apart.room_count,
    new_apart.type_of_settlement,
    new_apart.rank,
    new_apart.floor,
    new_apart.rsm_apart_id,
    new_apart.status_id;