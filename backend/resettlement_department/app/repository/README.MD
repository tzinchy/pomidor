SWITCH APARTS IS POSTGRESS FUNCTION: 


CREATE OR REPLACE FUNCTION switch_apartments(first_apartment_id INT, second_apartment_id INT)
RETURNS VOID AS $$
DECLARE
    temp_new_aparts TEXT;
BEGIN
    -- Сохраняем значение new_aparts для первого apartment_id
    SELECT new_aparts INTO temp_new_aparts
    FROM offer
    WHERE apartment_id = first_apartment_id;

    -- Обновляем первую квартиру значением из второй
    UPDATE offer
    SET new_aparts = (SELECT new_aparts FROM offer WHERE apartment_id = second_apartment_id)
    WHERE apartment_id = first_apartment_id;

    -- Обновляем вторую квартиру сохранённым значением
    UPDATE offer
    SET new_aparts = temp_new_aparts
    WHERE apartment_id = second_apartment_id;
END;
$$ LANGUAGE plpgsql;