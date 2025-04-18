## Триггер sync_status_from_offer
### Функция
```sql
CREATE OR REPLACE FUNCTION public.sync_status_from_offer()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$DECLARE
    priority_status_id INTEGER;
    status_record RECORD;
BEGIN
    -- 1. Инициализация приоритетного статуса
    priority_status_id := 1; -- По умолчанию "Согласие" (1)
    
    -- 2. Определяем приоритетный статус из new_aparts
    FOR status_record IN 
        SELECT (value->>'status_id')::INTEGER as status_id 
        FROM jsonb_each(NEW.new_aparts)
        WHERE value->>'status_id' IS NOT NULL
    LOOP
        -- Обновленная приоритетная цепочка:
        -- 3 (Суд) > 7 > 2 > 6 > 4 > 5 > 9 > 10 > 1
        IF status_record.status_id = 3 THEN 
            priority_status_id := 3;
            EXIT; -- Суд имеет наивысший приоритет
        ELSIF status_record.status_id = 7 AND priority_status_id < 7 THEN
            priority_status_id := 7;
        ELSIF status_record.status_id = 2 AND priority_status_id < 2 THEN
            priority_status_id := 2;
        ELSIF status_record.status_id = 6 AND priority_status_id < 6 THEN
            priority_status_id := 6;
        ELSIF status_record.status_id = 4 AND priority_status_id < 4 THEN
            priority_status_id := 4;
        ELSIF status_record.status_id = 5 AND priority_status_id < 5 THEN
            priority_status_id := 5;
        ELSIF status_record.status_id = 9 AND priority_status_id < 9 THEN
            priority_status_id := 9;
        ELSIF status_record.status_id = 10 AND priority_status_id < 10 THEN
            priority_status_id := 10;
        END IF;
    END LOOP;

    -- 3. Обновляем статус в самом offer
    NEW.status_id := priority_status_id;
    
    -- 4. Обновляем связанные квартиры в new_apart
    IF NEW.new_aparts IS NOT NULL THEN
        UPDATE new_apart na
        SET status_id = CASE 
            WHEN (NEW.new_aparts->na.new_apart_id::text->>'status_id')::INTEGER = 2 THEN 6 -- Отказ → Ожидание
            WHEN (NEW.new_aparts->na.new_apart_id::text->>'status_id')::INTEGER = 6 THEN 6 -- Сохраняем Ожидание
            ELSE (NEW.new_aparts->na.new_apart_id::text->>'status_id')::INTEGER
        END,
        updated_at = NOW()
        WHERE na.new_apart_id IN (
            SELECT jsonb_object_keys(NEW.new_aparts)::BIGINT
        );
    END IF;
    
    -- 5. Обновляем статус в old_apart
    UPDATE old_apart
    SET status_id = NEW.status_id
    WHERE affair_id = NEW.affair_id;
    
    RETURN NEW;
END;$function$
```
### Триггер
```sql
CREATE OR REPLACE TRIGGER trg_order_decisions
AFTER INSERT OR UPDATE ON public.order_decisions
FOR EACH ROW
EXECUTE FUNCTION public.apply_order_status();
```