## Триггер sync_apart_status_on_offer_delete
### Функция
```sql
CREATE OR REPLACE FUNCTION public.sync_apart_status_on_offer_delete()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    o_affair_id bigint := OLD.affair_id;
    prev_new_aparts jsonb;
BEGIN
    -- Если это был последний offer
    IF NOT EXISTS (
        SELECT 1 FROM offer WHERE affair_id = o_affair_id AND offer_id > OLD.offer_id
    ) THEN

        -- Берем предыдущий offer целиком
        SELECT new_aparts INTO prev_new_aparts
        FROM offer
        WHERE affair_id = o_affair_id AND offer_id < OLD.offer_id
        ORDER BY offer_id DESC
        LIMIT 1;

        IF FOUND AND prev_new_aparts IS NOT NULL THEN

            -- Массово обновим все new_apart, извлекая new_apart_id и status_id
            UPDATE new_apart na
            SET status_id = (js.value->>'status_id')::int
            FROM jsonb_each(prev_new_aparts) AS js(key, value)
            WHERE na.new_apart_id = js.key::bigint;

            -- Приоритетный статус: выберем наивысший из всех status_id
            UPDATE old_apart
            SET status_id = (
                SELECT CASE
                    WHEN 3  = ANY(status_list) THEN 3
                    WHEN 7  = ANY(status_list) THEN 7
                    WHEN 2  = ANY(status_list) THEN 2
                    WHEN 6  = ANY(status_list) THEN 6
                    WHEN 4  = ANY(status_list) THEN 4
                    WHEN 5  = ANY(status_list) THEN 5
                    WHEN 9  = ANY(status_list) THEN 9
                    WHEN 10 = ANY(status_list) THEN 10
                    ELSE 1
                END
                FROM (
                    SELECT ARRAY_AGG(DISTINCT (js.value->>'status_id')::int) AS status_list
                    FROM jsonb_each(prev_new_aparts) AS js
                ) subq
            )
            WHERE affair_id = o_affair_id;

        ELSE
            -- Предыдущего offer нет — дефолт
            UPDATE old_apart
            SET status_id = 8
            WHERE affair_id = o_affair_id;

            -- Обновим все new_apart из OLD.new_aparts
            IF OLD.new_aparts IS NOT NULL AND jsonb_typeof(OLD.new_aparts) = 'object' THEN
                UPDATE new_apart na
                SET status_id = 11
                FROM jsonb_object_keys(OLD.new_aparts) AS js(key)
                WHERE na.new_apart_id = js.key::bigint;
            END IF;
        END IF;
    END IF;

    RETURN OLD;
END;
$function$
```
### Триггер
```sql
CREATE OR REPLACE TRIGGER after_offer_delete_trigger
AFTER DELETE ON public.offer
FOR EACH ROW
EXECUTE FUNCTION public.sync_apart_status_on_offer_delete();
```