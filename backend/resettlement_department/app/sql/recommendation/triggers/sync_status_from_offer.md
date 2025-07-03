## Триггер sync_status_from_offer
### Функция
```sql
CREATE OR REPLACE FUNCTION public.sync_status_from_offer()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$DECLARE
    final_status_id INTEGER := 7; -- По умолчанию "Ждет одобрения"
    apart_id BIGINT;
    apart_status_id INTEGER;
    statuses INTEGER[];
    offer_with_order_id INTEGER := NULL; 
    v_status_id INTEGER := NULL;
    -- Флаги для проверки наличия статусов
    has_refusal BOOLEAN;
    has_approval_wait BOOLEAN;
    has_agreement BOOLEAN;
    has_waiting BOOLEAN;
    has_court BOOLEAN;
    has_prepare_viewing BOOLEAN;
    has_mfr_compensation BOOLEAN;
    has_mfr_compensation_out BOOLEAN;
    has_mfr_purchase BOOLEAN;
    has_mfr_out BOOLEAN;
    has_refusual_exit_from_the_court BOOLEAN;

BEGIN
    -- Собираем все уникальные статусы из квартир в оффере
    SELECT array_agg(DISTINCT (value->>'status_id')::INTEGER)
    INTO statuses
    FROM jsonb_each(NEW.new_aparts)
    WHERE value->>'status_id' IS NOT NULL;
    
    -- Устанавливаем итоговый статус оффера на основе статусов квартир
    IF statuses IS NOT NULL AND array_length(statuses, 1) > 0 THEN
        -- Проверяем наличие каждого типа статуса
        has_refusal := (2 = ANY(statuses));
        has_refusual_exit_from_the_court := (17 = ANY(statuses));
        has_approval_wait := (7 = ANY(statuses));
        has_prepare_viewing := (16 = ANY(statuses));
        has_waiting := (6 = ANY(statuses));
        has_court := (3 = ANY(statuses));  
        has_mfr_purchase := (5 = ANY(statuses));
        has_mfr_out := (9 = ANY(statuses));
        has_mfr_compensation := (4 = ANY(statuses));
        has_mfr_compensation_out := (10 = ANY(statuses));
        has_agreement := (1 = ANY(statuses));
        
        -- Применяем правила статусной модели по четкому приоритету (сверху вниз)
        IF has_refusal OR has_refusual_exit_from_the_court THEN
            final_status_id := 2;
        ELSIF has_approval_wait THEN
            final_status_id := 7;
        ELSIF has_prepare_viewing THEN
            final_status_id := 16;
        ELSIF has_waiting THEN
            final_status_id := 6;
        ELSIF has_court THEN
            final_status_id := 3;
        ELSIF has_mfr_purchase THEN 
            final_status_id := 5;
        ELSIF has_mfr_out THEN
            final_status_id := 9;
        ELSIF has_mfr_compensation THEN
            final_status_id := 4;
        ELSIF has_mfr_compensation_out THEN
            final_status_id := 10;
        ELSIF has_agreement THEN
            final_status_id := 1;
        END IF;
    END IF;
    
    -- Устанавливаем предварительный статус оффера
    NEW.status_id := final_status_id;
    
    -- Проверяем, есть ли оффер с выпиской (order_id) по этому делу
    SELECT max(offer_id) INTO offer_with_order_id FROM offer 
    WHERE affair_id = NEW.affair_id AND order_id IS NOT NULL AND offer_id != NEW.offer_id;

    -- ИСПРАВЛЕНИЕ ЛОГИКИ: Применяем специальные правила при наличии выписки
    IF offer_with_order_id IS NOT NULL THEN
        SELECT status_id INTO v_status_id FROM offer WHERE offer_id = offer_with_order_id;
        
        -- Правило 1: Если новый статус "Отказ" (2), то возвращаем статус из старой выписки.
        IF NEW.status_id = 2 THEN
            NEW.status_id := v_status_id;
            
        -- Правило 2: Если статус в старой выписке "Суд" (3).
        ELSIF v_status_id = 3 THEN
            -- "Суд" имеет приоритет над всем, КРОМЕ нового "Согласия" (1) и активных статусов (6,7,16).
            -- Тест `1 -> 3 expected 1` показывает, что `1` должен остаться.
            IF NEW.status_id NOT IN (1, 6, 7, 16) THEN
                NEW.status_id := 3;
            END IF;

        -- Правило 3: Если статус в старой выписке МФР (4, 5, 9, 10).
        ELSIF v_status_id IN (4, 5, 9, 10) THEN
            -- Статус МФР из выписки "прилипает" и заменяет новый, если новый не является
            -- более приоритетным (Суд или активные статусы).
            IF NEW.status_id NOT IN (3, 6, 7, 16) THEN
                NEW.status_id := v_status_id;
            END IF;
        END IF;
    END IF;
    
    -- Обновляем статусы квартир
    FOR apart_id IN 
        SELECT key::BIGINT FROM jsonb_each(NEW.new_aparts)
    LOOP
        apart_status_id := (NEW.new_aparts->apart_id::text->>'status_id')::INTEGER;
        
        IF apart_status_id IN (2, 17) THEN
            UPDATE new_apart SET status_id = 11, updated_at = NOW() WHERE new_apart_id = apart_id;
        ELSE
            UPDATE new_apart SET status_id = apart_status_id, updated_at = NOW() WHERE new_apart_id = apart_id;
        END IF;
    END LOOP;
    
    -- Обновляем связанный old_apart
    UPDATE old_apart
    SET status_id = NEW.status_id, updated_at = NOW()
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