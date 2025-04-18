## Триггер apply_order_status

### Функция
```sql
CREATE OR REPLACE FUNCTION public.apply_order_status()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$DECLARE
    order_status_id INTEGER;
    old_update_count INTEGER;
    offer_update_count INTEGER;
    old_status INTEGER;
    trimmed_collateral TEXT;
    trimmed_article TEXT;
    v_order_id BIGINT;
BEGIN
    -- Подготовка данных
    trimmed_article := TRIM(NEW.article_code);
    trimmed_collateral := TRIM(NEW.collateral_type);

    -- 2. Определение статуса
    order_status_id := CASE 
        WHEN trimmed_article = '97/70' THEN 3
        WHEN trimmed_article = '9711' THEN 1
        WHEN trimmed_article = '9715' THEN 1
        WHEN trimmed_article = '9736' THEN 1
        WHEN trimmed_article = '9723' THEN 1
        WHEN trimmed_article = '9712' THEN 1
        WHEN trimmed_article = '7001' THEN 1
        WHEN trimmed_article = '7002' AND trimmed_collateral = 'ППд' THEN 5
        WHEN trimmed_article = '7002' AND trimmed_collateral LIKE 'ППк%' THEN 4
        WHEN trimmed_article = '7002' AND trimmed_collateral = 'ППв' THEN 9
        WHEN trimmed_article = '7002' AND trimmed_collateral LIKE '%ППвк%' THEN 10
        WHEN trimmed_article = '70' OR 
             NEW.accounting_article LIKE '70%Реновация%' OR 
             NEW.accounting_article LIKE '70%Переселение%' THEN 1
        ELSE NULL
    END;

	UPDATE offer
	SET
		order_id = NEW.order_id,
		updated_at = NOW()
	WHERE
		affair_id = NEW.affair_id
		AND offer.new_aparts IS NOT NULL
		AND jsonb_typeof(offer.new_aparts) = 'object'
		AND jsonb_typeof(NEW.area_id) = 'object'
		AND offer.new_aparts ?& (
			SELECT
				array_agg(key)
			FROM
				jsonb_object_keys(NEW.area_id) key
		);
			
    IF order_status_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- 5. Обновляем статус в offer.new_aparts а потом другой триггер раскидает статусы
	--     на new_apart и old_apart 
	UPDATE offer
	SET
		new_aparts = (
			SELECT
				COALESCE(jsonb_object_agg(key, jsonb_set(value, '{status_id}', to_jsonb(order_status_id))), '{}'::jsonb)
			FROM
				jsonb_each(COALESCE(offer.new_aparts, '{}'::jsonb))
		),
		updated_at = NOW()
	WHERE
		offer_id IN (
			SELECT
				MAX(offer_id)
			FROM
				offer
			WHERE
				affair_id = NEW.affair_id
			GROUP BY
				affair_id
		);


    RETURN NEW;
END;$function$
```

### Триггер
```sql
CREATE OR REPLACE TRIGGER trigger_sync_from_offer
BEFORE INSERT OR UPDATE ON public.offer
FOR EACH ROW
EXECUTE FUNCTION public.sync_status_from_offer();
```
