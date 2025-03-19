WITH changeStatus AS (
    SELECT status_id FROM status WHERE status = :status
),
oldApartId AS (
    SELECT (:apart_id)::bigint AS apart_id
)
UPDATE public.offer
SET
    status_id = (SELECT status_id FROM changeStatus), 
    new_aparts = (
        SELECT jsonb_object_agg(key, jsonb_set(value, '{status_id}', to_jsonb((SELECT status_id FROM changeStatus)), false))
        FROM jsonb_each(new_aparts)
    ) 
WHERE affair_id = (SELECT apart_id FROM oldApartId)
AND created_at = (
    SELECT MAX(created_at) 
    FROM public.offer 
    WHERE affair_id = (SELECT apart_id FROM oldApartId)
);
