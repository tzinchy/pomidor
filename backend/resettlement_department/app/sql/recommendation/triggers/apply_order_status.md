## Триггер apply_order_status

### Функция
```sql
CREATE OR REPLACE FUNCTION public.apply_order_status()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$DECLARE
    v_order_status_id INTEGER;
    v_new_apart_id BIGINT;
    v_count_matches INTEGER;
    v_trimmed_collateral TEXT := TRIM(NEW.collateral_type);
    v_trimmed_article TEXT := TRIM(NEW.article_code);
    v_existing_offer_id BIGINT;
BEGIN
    -- 1. Определение статуса
	
    v_order_status_id := CASE 
		WHEN NEW.is_cancelled = True AND v_trimmed_article = '97/70' THEN  17
		WHEN NEW.is_cancelled = True THEN  2
        WHEN v_trimmed_article = '97/70' THEN 3
        WHEN v_trimmed_article IN ('9711', '9715', '9736', '9723', '9712', '7001') THEN 1
        WHEN v_trimmed_article = '7002' AND v_trimmed_collateral = 'ППд' THEN 5
        WHEN v_trimmed_article = '7002' AND v_trimmed_collateral LIKE 'ППк%' THEN 4
        WHEN v_trimmed_article = '7002' AND v_trimmed_collateral = 'ППв' THEN 9
        WHEN v_trimmed_article = '7002' AND v_trimmed_collateral LIKE '%ППвк%' THEN 10
        WHEN v_trimmed_article = '70'
             OR NEW.accounting_article LIKE '70%Реновация%'
             OR NEW.accounting_article LIKE '70%Переселение%' THEN 1
        ELSE NULL
    END;

    -- Если статус не определен, завершаем выполнение
    IF v_order_status_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- 2. Поиск new_apart_id через cad_num, unom/un_kv и area_id
    IF NEW.cad_num IS NOT NULL THEN
        SELECT new_apart_id INTO v_new_apart_id
        FROM new_apart
        WHERE cad_num = NEW.cad_num
        LIMIT 1;
    END IF;

    IF v_new_apart_id IS NULL AND NEW.unom IS NOT NULL AND NEW.un_kv IS NOT NULL THEN
        SELECT new_apart_id INTO v_new_apart_id
        FROM new_apart
        WHERE unom = NEW.unom AND un_kv = NEW.un_kv
        LIMIT 1;
    END IF;

    IF v_new_apart_id IS NULL AND NEW.area_id IS NOT NULL THEN
        SELECT new_apart_id INTO v_new_apart_id
        FROM new_apart 
        WHERE rsm_apart_id = (SELECT key::bigint FROM jsonb_each_text(NEW.area_id) LIMIT 1)
        LIMIT 1;
    END IF;

    -- Если не нашли new_apart_id, выходим без изменений
    IF v_new_apart_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- 3. Проверяем существование записи с таким affair_id и new_apart_id
    SELECT offer_id INTO v_existing_offer_id
    FROM (
        SELECT offer_id 
        FROM offer, jsonb_each_text(new_aparts) 
        WHERE affair_id = NEW.affair_id AND v_new_apart_id = key::bigint
        ORDER BY offer_id DESC
        LIMIT 1
    ) subq;

    -- 4. Обновление или вставка в offer
	IF v_existing_offer_id IS NOT NULL THEN 
	    -- Обновляем существующую запись
	    UPDATE offer
	    SET 
	        new_aparts = jsonb_set(
	            new_aparts, 
	            ARRAY[v_new_apart_id::text, 'status_id'], 
	            to_jsonb(v_order_status_id)
	        ),
	        order_id = NEW.order_id,
	        order_ids = CASE 
	            WHEN order_ids IS NULL THEN ARRAY[NEW.order_id]::integer[]
	            WHEN NOT (NEW.order_id = ANY(order_ids)) THEN array_append(order_ids, NEW.order_id)
	            ELSE order_ids
	        END,
	        updated_at = NOW()
	    WHERE offer_id = v_existing_offer_id;
	    
	    -- Обновляем статус в old_apart (исправленная строка)
	    UPDATE old_apart 
	    SET order_status_id = v_order_status_id
	    WHERE NEW.affair_id = affair_id;

		UPDATE new_apart 
		SET order_status_id = v_order_status_id 
		WHERE new_apart_id = v_new_apart_id;
	    
	    -- Здесь можно добавить логику для обработки отсутствующих выписок
	    -- Например:
	    -- INSERT INTO statements (offer_id, statement_data)
	    -- SELECT v_existing_offer_id, NEW.statement_data
	    -- WHERE NOT EXISTS (SELECT 1 FROM statements WHERE offer_id = v_existing_offer_id AND ...);
	END IF;
    
    IF v_existing_offer_id IS NULL and NEW.is_cancelled = False THEN 
        INSERT INTO offer (affair_id, order_id, new_aparts, created_at, updated_at)
        VALUES (
            NEW.affair_id,
            NEW.order_id,
            jsonb_build_object(
                v_new_apart_id::text, 
                jsonb_build_object('status_id', v_order_status_id)
            ),
            NOW(),
            NOW()
        );
    END IF;
	

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
