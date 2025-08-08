## Триггер sync_apart_status_on_offer_delete
### Функция
```sql
CREATE OR REPLACE FUNCTION public.sync_apart_status_on_offer_delete()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    o_affair_id bigint := OLD.affair_id;
    prev_offer_id bigint;
BEGIN
    -- Обновим все new_apart из OLD.new_aparts
    IF OLD.new_aparts IS NOT NULL AND jsonb_typeof(OLD.new_aparts) = 'object' THEN
        UPDATE new_apart na
        SET status_id = 11
        FROM jsonb_object_keys(OLD.new_aparts) AS js(key)
        WHERE na.new_apart_id = js.key::bigint;
    END IF;
    -- Если это был актуальный offer
    IF NOT EXISTS (
        SELECT 1 FROM offer WHERE affair_id = o_affair_id AND offer_id > OLD.offer_id
    ) THEN
		-- Вызываем триггер на обновление статуса у прошлого offer
        SELECT offer_id INTO prev_offer_id
	    FROM offer
	    WHERE affair_id = o_affair_id AND offer_id < OLD.offer_id
	    ORDER BY offer_id DESC
	    LIMIT 1;
	    
	    IF prev_offer_id IS NOT NULL THEN
	        UPDATE offer 
	        SET updated_at = NOW()
	        WHERE offer_id = prev_offer_id;
	    ELSE
	        -- Нет предыдущего offer → выполняем дефолтное действие
	        UPDATE old_apart
	        SET status_id = 8
	        WHERE affair_id = o_affair_id;
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