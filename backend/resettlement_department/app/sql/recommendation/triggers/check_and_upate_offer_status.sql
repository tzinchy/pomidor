
DECLARE
    status_ids JSONB;
    selected_status TEXT;
BEGIN
    -- Собираем все status_id из new_aparts
    status_ids := (
        SELECT jsonb_agg(value->>'status_id')
        FROM jsonb_each(NEW.new_aparts)
    );

    -- Проверяем приоритеты статусов
    IF '3' = ANY(SELECT jsonb_array_elements_text(status_ids)) THEN
        selected_status := 'Суд'; -- Самый высокий приоритет
    ELSIF '7' = ANY(SELECT jsonb_array_elements_text(status_ids)) THEN
        selected_status := 'Ждёт одобрения'; -- Второй по приоритету
    ELSIF '2' = ANY(SELECT jsonb_array_elements_text(status_ids)) THEN
        selected_status := 'Отказ'; -- Третий по приоритету
    ELSIF '4' = ANY(SELECT jsonb_array_elements_text(status_ids)) THEN
        selected_status := 'Фонд компенсация'; -- Четвертый по приоритету
    ELSIF '5' = ANY(SELECT jsonb_array_elements_text(status_ids)) THEN
        selected_status := 'Фонд докупка'; -- Пятый по приоритету
    ELSIF '6' = ANY(SELECT jsonb_array_elements_text(status_ids)) THEN
        selected_status := 'Ожидание'; -- Шестой по приоритету
    ELSE
        selected_status := 'Согласие'; -- Самый низкий приоритет
    END IF;

    -- Обновляем offer.status_id
    UPDATE offer
    SET status_id = (SELECT status_id FROM status WHERE status = selected_status)
    WHERE offer_id = NEW.offer_id;

    RETURN NEW;
END;
